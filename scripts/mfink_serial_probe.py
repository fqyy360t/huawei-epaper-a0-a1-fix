import json
import sys
import time
import urllib.request

import serial

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))

for baud in (115200, 921600, 74880):
    try:
        s = serial.Serial("COM16", baud, timeout=0.2)
    except Exception as exc:
        print("open", baud, "failed", exc)
        continue
    print("=== BAUD", baud, "===", flush=True)
    try:
        req = urllib.request.Request("http://192.168.4.1/api/clear?cycles=2", method="POST")
        with opener.open(req, timeout=10) as r:
            print("clear:", r.read().decode("utf-8", "replace"), flush=True)
        data = b"".join(s.read(4096) for _ in range(200))
        text = data.decode("utf-8", "replace")
        print(text[-20000:], flush=True)
    except Exception as exc:
        print("probe error", exc)
    finally:
        s.close()
