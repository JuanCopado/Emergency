"""Held-out image variations. Report exact reviewed candidates, misses and errors."""
from test_blood_gas_multiformat import picture,encoded,extract
from PIL import ImageDraw,ImageFilter
import json
img=picture(["pH 7,18","pCO2 54 mmHg","Na 152 mmol/L"])
glare=img.copy()
ImageDraw.Draw(glare).rectangle((99,12,144,180),fill="white")
expected={"pH":("7,18",""),"pCO2":("54","mmHg"),"Na":("152","mmol/L")}
report={}
for name,example in (("clear",img),("rotated",img.rotate(90,expand=True)),
                     ("blur",img.filter(ImageFilter.GaussianBlur(3))),
                     ("crop",img.crop((0,0,160,102))),("glare",glare)):
    rows=extract(encoded(example,"JPEG"))[0]["fields"]
    values={r["name"]:(r["number"],r["unit"]) for r in rows}
    report[name]={"expected":expected,"observed":values,
                  "exact":sum(values.get(k)==v for k,v in expected.items()),
                  "abstained":len(expected.keys()-values.keys()),
                  "wrong":sum(v!=expected.get(k) for k,v in values.items())}
print(json.dumps(report,indent=2))
