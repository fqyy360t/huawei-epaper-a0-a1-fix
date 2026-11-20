#!/usr/bin/env python3
"""Poll MF-INK /api/info until a refresh finishes."""
import json
import sys
import time
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
seconds = int(sys.argv[1]) if len(sys.argv) > 1 else 90
seen_busy = False

for i in range(seconds):
    with opener.open("http://192.168.4.1/api/info", timeout=5) as r:
        info = json.loads(r.read().decode("utf-8"))
    busy = info.get("busy")
    last = info.get("last")
    seen_busy = seen_busy or bool(busy)
    print(i, "busy=", busy, "seq=", info.get("seq"), "last=", last, flush=True)
    if last == 0 or (seen_busy and not busy and i > 5):
        break
    time.sleep(1)
