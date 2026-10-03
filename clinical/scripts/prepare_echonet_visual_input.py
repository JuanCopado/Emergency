#!/usr/bin/env python3
"""Deterministic 32-frame EchoNet sampling with no label-dependent selection."""

import argparse
import json
from pathlib import Path

def frame_indices(total_frames, n=32):
    if total_frames < n:
        raise ValueError(f"video has {total_frames} frames; need >={n}")
    if n < 2:
        raise ValueError("n must be >=2")
    return [round(i*(total_frames-1)/(n-1)) for i in range(n)]

def extract(video_path, output_dir, n=32):
    import cv2
    cap=cv2.VideoCapture(str(video_path))
    if not cap.isOpened(): raise ValueError("cannot open video")
    total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    idxs=frame_indices(total,n)
    out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
    wanted=set(idxs); written=[]
    i=0
    while True:
        ok,frame=cap.read()
        if not ok: break
        if i in wanted:
            name=f"frame-{len(written):02d}-src-{i:06d}.png"
            cv2.imwrite(str(out/name),frame)
            written.append({"sequence_index":len(written),"source_frame_index":i,"image_file":name})
        i+=1
    cap.release()
    if len(written)!=n: raise ValueError(f"decoded {len(written)}/{n} requested frames")
    meta={"schema_version":"1.0","sampling":"uniform_full_video","frame_count_source":total,
          "frame_count_output":n,"frames":written}
    (out/"frame_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    return meta

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("video",type=Path); p.add_argument("output_dir",type=Path)
    p.add_argument("--frames",type=int,default=32)
    a=p.parse_args(); print(json.dumps(extract(a.video,a.output_dir,a.frames)))
