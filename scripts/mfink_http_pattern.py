#!/usr/bin/env python3
"""MF-INK V1.0.4 HTTP frame test: set panel mode and push an asymmetric pattern."""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

import cv2
import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = "http://192.168.4.1"
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def get_json(path):
    with OPENER.open(BASE + path, timeout=8) as r:
        return json.loads(r.read().decode("utf-8"))


def post_settings(panel, a1_mode):
    data = urllib.parse.urlencode({"panel": panel, "a1_mode": a1_mode}).encode("ascii")
    req = urllib.request.Request(BASE + "/api/settings", data=data, method="POST",
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with OPENER.open(req, timeout=8) as r:
        return r.status, r.read().decode("utf-8", "replace")


def crc16_ccitt(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc


def make_pattern(w, h):
    # 0=black 1=white 2=yellow 3=red
    idx = np.ones((h, w), dtype=np.uint8)

    def rect(x0, y0, x1, y1, color):
        idx[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = color

    rect(0.05, 0.07, 0.39, 0.43, 0)  # top-left black
    rect(0.61, 0.07, 0.95, 0.43, 2)  # top-right yellow
    rect(0.05, 0.57, 0.39, 0.93, 3)  # bottom-left red
    rect(0.61, 0.57, 0.95, 0.93, 0)  # bottom-right black
    return idx


def make_labels(w, h):
    canvas = np.full((h, w), 255, dtype=np.uint8)
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = max(2.0, w / 260.0)
    thick = max(4, int(w / 120))
    cv2.putText(canvas, "TL", (int(w * 0.08), int(h * 0.25)), font, scale, 0, thick, cv2.LINE_AA)
    cv2.putText(canvas, "TR", (int(w * 0.62), int(h * 0.25)), font, scale, 0, thick, cv2.LINE_AA)
    cv2.putText(canvas, "BL", (int(w * 0.08), int(h * 0.78)), font, scale, 0, thick, cv2.LINE_AA)
    cv2.putText(canvas, "BR", (int(w * 0.62), int(h * 0.78)), font, scale, 0, thick, cv2.LINE_AA)
    cv2.rectangle(canvas, (8, 8), (w - 9, h - 9), 0, thick)
    return np.where(canvas < 128, 0, 1).astype(np.uint8)  # black=0, white=1


def pack_2bpp(idx):
    # MoInk/MF-INK packIdx contract: source row and byte order are both reversed.
    h, w = idx.shape
    assert w % 4 == 0
    rb = w // 4
    flat = idx.reshape(-1)
    out = np.zeros((h, rb), dtype=np.uint8)
    for r in range(h):
        ro = (h - 1 - r) * w
        for xb in range(rb):
            xa = w - 4 - (xb << 2)
            out[r, xb] = ((flat[ro + xa + 3] << 6) | (flat[ro + xa + 2] << 4) |
                          (flat[ro + xa + 1] << 2) | flat[ro + xa])
    return out.tobytes()


def frame_body(payload, panel_id, mode_id, w, h):
    crc = crc16_ccitt(payload)
    hdr = bytearray(16)
    hdr[0], hdr[1] = 0xA5, 0x5A
    hdr[2] = mode_id
    hdr[3] = panel_id
    hdr[4:6] = w.to_bytes(2, "big")
    hdr[6:8] = h.to_bytes(2, "big")
    hdr[8:12] = len(payload).to_bytes(4, "big")
    hdr[12:14] = crc.to_bytes(2, "big")
    return bytes(hdr) + payload


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", type=int, choices=(1, 2), default=1,
                    help="A1 driver mode: 1=768x552, 2=800x600")
    ap.add_argument("--labels", action="store_true", help="send TL/TR/BL/BR labels instead of color blocks")
    args = ap.parse_args()

    before = get_json("/api/info")
    print("BEFORE:", json.dumps(before, ensure_ascii=False))
    print("SETTINGS:", post_settings(1, args.mode))

    w, h = (768, 552) if args.mode == 1 else (800, 600)
    mode_id = 1 if args.mode == 1 else 2
    src = make_labels(w, h) if args.labels else make_pattern(w, h)
    payload = pack_2bpp(src)
    body = frame_body(payload, 1, mode_id, w, h)
    tag = "labels" if args.labels else "pattern"
    path = "C:/Users/fqyy3/camframes/mfink_%s_%dx%d.bin" % (tag, w, h)
    with open(path, "wb") as f:
        f.write(body)
    print("FRAME:", path, len(body), "bytes")

    req = urllib.request.Request(BASE + "/api/frame", data=body, method="POST",
                                 headers={"Content-Type": "application/octet-stream"})
    with OPENER.open(req, timeout=40) as r:
        print("UPLOAD:", r.status, r.read().decode("utf-8", "replace"))

    seq0 = before.get("seq")
    for i in range(45):
        time.sleep(1)
        info = get_json("/api/info")
        if (not info.get("busy")) and (info.get("seq") != seq0 or i >= 30):
            print("DONE:", json.dumps(info, ensure_ascii=False))
            return
    print("TIMEOUT:", json.dumps(info, ensure_ascii=False))


if __name__ == "__main__":
    main()
