import io
import os
import json
import sys
import unittest
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from blood_gas_review import extract,interpret

def synthetic_font():
    return ImageFont.truetype(os.getenv("BG_TEST_FONT", "arial.ttf"), 32)

def picture(lines):
    img=Image.new("RGB",(580,220),"white")
    draw=ImageDraw.Draw(img)
    font=synthetic_font()
    for i,line in enumerate(lines):
        draw.text((20,15+i*52),line,font=font,fill="black")
    return img

def encoded(img,fmt):
    out=io.BytesIO()
    img.save(out,format=fmt)
    return out.getvalue()

def pdf(groups, scanned=False):
    out=io.BytesIO()
    c=canvas.Canvas(out,pagesize=(580,220))
    for lines in groups:
        if scanned:
            c.drawImage(ImageReader(picture(lines)),0,0,580,220)
        else:
            for i,line in enumerate(lines):
                c.drawString(20,190-i*32,line)
        c.showPage()
    c.save()
    return out.getvalue()

class Validation(unittest.TestCase):
    def test_formats(self):
        lines=["pH 7.28","Na 141 mmol/L","Cl 103 mmol/L"]
        for name,data in [('digital',pdf([lines])),('scan',pdf([lines],True))]+[
                (f,encoded(picture(lines),f)) for f in ('PNG','JPEG','WEBP','TIFF')]:
            with self.subTest(format=name):
                fields=extract(data)[0]['fields']
                print(json.dumps(dict(format=name,values=[[f['name'],f['number'],f['unit']] for f in fields])))
                self.assertEqual([(f['name'],f['number'],f['unit']) for f in fields],
                                 [('pH','7.28',''),('Na','141','mmol/L'),('Cl','103','mmol/L')])
    def test_pages(self):
        pages=extract(pdf([['pH 7,41'],['pH 7.02']]))
        self.assertEqual([p['fields'][0]['number'] for p in pages],['7,41','7.02'])
    def test_confirmation(self):
        fields=extract(pdf([['pH 7.21','HCO3 10 mmol/L','Na 140 mmol/L','Cl 101 mmol/L','pO2 80 mmHg','FiO2 40 %']]))[0]['fields']
        with self.assertRaises(ValueError):interpret(fields,'arterial')
        for f in fields:f['review']='confirmed'
        self.assertEqual(interpret(fields,'arterial')['anion_gap_mmol_l'],29)
        self.assertEqual(interpret(fields,'arterial')['pao2_fio2_ratio_mm_hg'],200)
        self.assertNotIn('pao2_fio2_ratio_mm_hg',interpret(fields,'venosa'))
        with self.assertRaises(ValueError):interpret(fields+fields,'arterial')
    def test_invalid(self):
        for data in (b'',b'%PDF-broken',b'MZ123',b'X'*9000000):
            with self.assertRaises(Exception):extract(data)

    def test_two_explicit_samples_same_page(self):
        pages=extract(pdf([["Sample: A","pH 7.10","Na 142 mmol/L",
                            "Sample: B","pH 7.48","Na 138 mmol/L"]]))
        self.assertEqual([p["sample_label"] for p in pages],["A","B"])
        self.assertEqual([p["source_page"] for p in pages],[1,1])
        self.assertEqual([p["fields"][0]["number"] for p in pages],["7.10","7.48"])
        self.assertEqual([p["fields"][1]["number"] for p in pages],["142","138"])

    def test_duplicate_without_headers_abstains(self):
        pages=extract(pdf([["pH 7.10","pH 7.48"]]))
        self.assertTrue(pages[0]["blocked"])
        self.assertEqual(pages[0]["fields"],[])

    def test_unreadable_unit_is_not_accepted(self):
        fields=extract(pdf([["pCO2 54"]]))[0]["fields"]
        self.assertEqual(fields[0]["legibility"],"unit_unreadable")
        fields[0]["review"]="confirmed"
        with self.assertRaises(ValueError):interpret(fields,"arterial")

    def test_mixed_pdf_layers_warn(self):
        out=io.BytesIO()
        c=canvas.Canvas(out,pagesize=(580,220))
        c.drawImage(ImageReader(picture(["pH 7.41"])),0,0,580,220)
        c.setFillAlpha(0)
        c.drawString(20,190,"pH 7.11")
        c.save()
        rows=extract(out.getvalue())[0]["fields"]
        self.assertEqual(rows[0]["review"],"discrepancy")
        self.assertEqual(rows[0]["raw"],"pH 7.11")

    @unittest.skipUnless(os.name == 'nt', 'Requires Windows Job Object containment; exercised by Windows OCR CI')
    def test_contained_worker(self):
        from blood_gas_worker import safe_extract
        for data in (pdf([["pH 7.42"]]), encoded(picture(["pH 7.42"]),"PNG")):
            pages=safe_extract(data)
            self.assertEqual(pages[0]["fields"][0]["number"],"7.42")

    def test_numbered_headers(self):
        pages=extract(pdf([["Sample 1","pH 7.10","Sample 2","Na 138 mmol/L"]]))
        self.assertEqual([p["sample_label"] for p in pages],["1","2"])
        self.assertEqual([[f["name"] for f in p["fields"]] for p in pages],[["pH"],["Na"]])

    def test_explicit_metadata_and_provenance(self):
        pages=extract(pdf([["pH 7.31 [measured]","HCO3 18 mmol/L [calculated]",
                           "Sample type: venous","Date: 2026-11-17","Flags: analyzer warning"]]))
        self.assertEqual([f["origin"] for f in pages[0]["fields"]],["measured","calculated"])
        self.assertEqual(pages[0]["fields"][0]["raw"],"pH 7.31 [measured]")
        self.assertEqual(pages[0]["metadata"][0]["value"],"venous")

    def test_encrypted_pdf_rejected(self):
        from pypdf import PdfReader,PdfWriter
        writer=PdfWriter()
        writer.append(PdfReader(io.BytesIO(pdf([["pH 7.41"]]))))
        writer.encrypt("synthetic-only")
        output=io.BytesIO()
        writer.write(output)
        with self.assertRaisesRegex(ValueError,"cifrado"):
            extract(output.getvalue())

    def test_page_and_pixel_limits(self):
        from blood_gas_review import PAGES,PIXELS
        with self.assertRaisesRegex(ValueError,"páginas"):
            extract(pdf([["pH 7.41"]]*(PAGES+1)))
        side=int(PIXELS**0.5)+1
        with self.assertRaisesRegex(ValueError,"Resolución"):
            extract(encoded(Image.new("RGB",(side,side)),"PNG"))

    @unittest.skipUnless(os.name == 'nt', 'Requires Windows Job Object containment; exercised by Windows OCR CI')
    def test_http_confirmation_and_revocation(self):
        import threading
        import urllib.request
        from urllib.error import HTTPError
        from blood_gas_local import make_server
        server=make_server()
        thread=threading.Thread(target=server.serve_forever)
        thread.start()
        def request(route, body):
            if not isinstance(body,bytes):
                body=json.dumps(body).encode()
            req=urllib.request.Request("http://"+server.address+route,body,
                headers={"X-Session":server.token,"Origin":"http://"+server.address,
                         "Content-Type":"application/octet-stream" if route == "/extract" else "application/json"})
            # Disable environment proxies even for loopback.
            with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(req) as res:
                return json.load(res)
        try:
            for data in (pdf([["pH 7.21"]]),pdf([["pH 7.21"]],True),
                         encoded(picture(["pH 7.21"]),"PNG"),
                         encoded(picture(["pH 7.21"]),"JPEG")):
                document=request("/extract",data)
                review=dict(ticket=document["ticket"],page=0,oneSample=True,
                            medicalConfirmed=True,areaConfirmed=True,
                            sample="arterial",rows=document["pages"][0]["fields"])
                with self.assertRaises(HTTPError):request("/review",review)
                for f in review["rows"]:
                    f["review"]="confirmed"
                    f["visualReviewed"]=True
                    f["transcribed"]=True
                for key in ('medicalConfirmed','areaConfirmed','oneSample'):
                    unconfirmed={**review,key:False}
                    with self.assertRaises(HTTPError):request('/review',unconfirmed)
                review['rows'][0]['visualReviewed']=False
                with self.assertRaises(HTTPError):request('/review',review)
                review['rows'][0]['visualReviewed']=True
                self.assertEqual(request("/review",review)["ph_state"],"acidemia")
                width=document['pages'][0]['width']
                height=document['pages'][0]['height']
                selected=request('/regions',dict(ticket=document['ticket'],regions=[dict(page=1,bbox=[0,0,width,height],label='única')]))
                self.assertNotEqual(selected['ticket'],document['ticket'])
                with self.assertRaises(HTTPError):request('/review',review)
                document=selected
                request("/reject",{"ticket":document["ticket"]})
                with self.assertRaises(HTTPError):request("/review",review)
            self.assertIsNone(server.source)
            self.assertEqual(server.pages,[])
            bad=urllib.request.Request('http://'+server.address+'/api/blood-gas/review',b'{}',headers={'X-Session':server.token,'Origin':'https://untrusted.invalid'})
            with self.assertRaises(HTTPError) as denied:
                urllib.request.build_opener(urllib.request.ProxyHandler({})).open(bad)
            self.assertEqual(denied.exception.code,403)
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

if __name__=='__main__':unittest.main()
