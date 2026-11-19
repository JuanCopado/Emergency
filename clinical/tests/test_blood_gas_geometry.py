import base64
import io
import unittest
from unittest.mock import patch
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from test_blood_gas_multiformat import encoded, extract, pdf, picture, synthetic_font
from blood_gas_geometry import original_box, validate_regions
from blood_gas_review import ocr_lines


class GeometryValidation(unittest.TestCase):
    def test_exact_original_crops_and_pdf_coordinates(self):
        for data in (encoded(picture(['pH 7.28','Na 141 mmol/L']), 'PNG'), pdf([['pH 7.28','Na 141 mmol/L']])):
            page=extract(data)[0]
            original=Image.open(io.BytesIO(base64.b64decode(page['preview'])))
            for field in page['fields']:
                self.assertTrue(field['bbox'])
                self.assertEqual(field['coordinate_space'],'rendered_original_pixels_top_left')
                crop=Image.open(io.BytesIO(base64.b64decode(field['crop'])))
                self.assertEqual(crop.tobytes(),original.crop(field['crop_bbox']).tobytes())
                self.assertLess(field['bbox'][1],field['bbox'][3])
            if page['method']=='text':
                self.assertLess(abs(page['fields'][0]['bbox'][0]-40),4)
                self.assertLess(page['fields'][0]['bbox'][1],80)
                self.assertEqual(page['fields'][0]['visual_check'],'matched')

    def test_two_columns_recovered_by_manual_regions(self):
        image=Image.new('RGB',(1200,250),'white')
        draw=ImageDraw.Draw(image); font=synthetic_font()
        for x,lines in ((20,['pH 7.10','Na 142 mmol/L']),(620,['pH 7.48','Na 138 mmol/L'])):
            for y,line in enumerate(lines): draw.text((x,20+y*60),line,font=font,fill='black')
        data=encoded(image,'PNG')
        pages=extract(data,[dict(page=1,bbox=[0,0,590,250],label='A'),dict(page=1,bbox=[600,0,1200,250],label='B')])
        self.assertEqual([p['sample_label'] for p in pages],['A','B'])
        self.assertEqual([[f['number'] for f in p['fields']] for p in pages],[['7.10','142'],['7.48','138']])
        self.assertTrue(all(p['manual_region'] for p in pages))
        self.assertGreater(pages[1]['fields'][0]['bbox'][0],600)

    def test_invalid_regions_fail_closed(self):
        for regions in ([],[dict(page=True,bbox=[0,0,100,100])], [dict(page=1,bbox=[0,0,float('nan'),100])],
                        [dict(page=1,bbox=[0,0,100,100]),dict(page=1,bbox=[50,0,150,100])]):
            with self.assertRaises(ValueError):validate_regions(regions)
        for region in (dict(page=2,bbox=[0,0,100,100]),dict(page=1,bbox=[0,0,10000,10000])):
            with self.assertRaises(ValueError):extract(encoded(picture(['pH 7.28']),'PNG'),[region])

    def test_all_pdf_text_is_visually_checked_without_image_objects(self):
        out=io.BytesIO(); c=canvas.Canvas(out,pagesize=(580,220))
        c.setFillAlpha(0); c.drawString(20,190,'pH 7.11'); c.save()
        row=extract(out.getvalue())[0]['fields'][0]
        self.assertEqual(row['visual_check'],'discrepancy')
        self.assertEqual(row['review'],'discrepancy')

    def test_visual_only_field_is_not_silently_lost(self):
        from reportlab.lib.utils import ImageReader
        out=io.BytesIO(); c=canvas.Canvas(out,pagesize=(580,220))
        c.drawImage(ImageReader(picture(['pH 7.28','Na 141 mmol/L'])),0,0,580,220)
        c.setFillAlpha(0); c.drawString(20,190,'pH 7.28'); c.save()
        page=extract(out.getvalue())[0]
        self.assertTrue(page['visual_extras'])
        self.assertTrue(any(f['name']=='Na' and f['visual_check']=='visual_only' for f in page['fields']))

    def test_all_orientations_evaluated_and_coordinates_return_to_original(self):
        def tsv(lines):
            return '\n'.join('5\t1\t1\t1\t%d\t1\t10\t%d\t90\t20\t95\t%s'%(i+1,i*30+10,line) for i,line in enumerate(lines))
        results=[dict(tsv=tsv(['pH 7.28'])),dict(tsv=tsv(['pH 7.28','Na 141 mmol/L'])),dict(tsv=''),dict(tsv='')]
        with patch('blood_gas_review.ocr_once',side_effect=results) as worker:
            lines,angle=ocr_lines(Image.new('RGB',(300,200)))
        self.assertEqual(worker.call_count,4)
        self.assertEqual(angle,90)
        self.assertEqual(len(lines),2)
        self.assertEqual(lines[0]['bbox'],[270,10,290,100])
        self.assertEqual(original_box([10,20,30,40],270,300,200),[20,170,40,190])

    def test_low_confidence_requires_explicit_transcription(self):
        from blood_gas_geometry import bind
        from blood_gas_review import parse
        rows=parse('pH 7.28',1)
        bind(rows,[dict(text='pH 7.28',bbox=[1,1,50,20],confidence=42)],picture(['pH 7.28']))
        self.assertEqual(rows[0]['legibility'],'low_confidence')
        self.assertEqual(rows[0]['review'],'discrepancy')

    def test_rotated_image_crops_are_original_pixels(self):
        image=picture(['pH 7.28','Na 141 mmol/L']).rotate(90,expand=True)
        page=extract(encoded(image,'PNG'))[0]
        self.assertEqual([f['number'] for f in page['fields']],['7.28','141'])
        for row in page['fields']:
            crop=Image.open(io.BytesIO(base64.b64decode(row['crop'])))
            self.assertEqual(crop.tobytes(),image.crop(row['crop_bbox']).tobytes())

if __name__=='__main__':unittest.main()
