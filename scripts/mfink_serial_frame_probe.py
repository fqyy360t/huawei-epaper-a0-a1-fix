import sys
import time
import urllib.request

import serial

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
frame = open("C:/Users/fqyy3/camframes/mfink_labels_768x552.bin", "rb").read()
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
s = serial.Serial("COM16", 115200, timeout=0.2)
try:
    time.sleep(0.3)
    req = urllib.request.Request("http://192.168.4.1/api/frame", data=frame, method="POST",
                                 headers={"Content-Type": "application/octet-stream"})
    with opener.open(req, timeout=30) as r:
        print("upload:", r.read().decode("utf-8", "replace"), flush=True)
    data = b"".join(s.read(4096) for _ in range(180))
    print(data.decode("utf-8", "replace")[-20000:], flush=True)
finally:
    s.close()
