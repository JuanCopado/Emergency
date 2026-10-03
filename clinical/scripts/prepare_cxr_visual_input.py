#!/usr/bin/env python3
"""Prepare model-facing CXR images without diagnosis-dependent enhancement."""

import argparse
import json
from pathlib import Path

def prepare_image(input_path, output_path, max_side=0):
    from PIL import Image, ImageOps
    src = Image.open(input_path)
    src = ImageOps.exif_transpose(src).convert("L")
    if src.width < 32 or src.height < 32:
        raise ValueError("invalid image dimensions")
    if max_side and max(src.size) > max_side:
        scale = max_side / max(src.size)
        new_size = (max(1, round(src.width*scale)), max(1, round(src.height*scale)))
        src = src.resize(new_size)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    src.save(output_path)
    return {"width": src.width, "height": src.height, "mode": "L"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("input",type=Path); p.add_argument("output",type=Path)
    p.add_argument("--max-side",type=int,default=0)
    a=p.parse_args(); result=prepare_image(a.input,a.output,a.max_side)
    print(json.dumps(result))
