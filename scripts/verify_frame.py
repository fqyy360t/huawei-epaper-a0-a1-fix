import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
paths = [
    "C:/Users/fqyy3/camframes/mfink_pattern_768x552.bin",
    "C:/Users/fqyy3/camframes/mfink_labels_768x552.bin",
]
for path in paths:
    data = open(path, "rb").read()
    hdr, payload = data[:16], data[16:]
    crc = 0xFFFF
    for x in payload:
        crc ^= x << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    print(path)
    print("  header:", hdr.hex())
    print("  payload_len:", len(payload), "crc_calc:", hex(crc), "crc_hdr:", hex(int.from_bytes(hdr[12:14], "big")))
    print("  payload_mean:", round(sum(payload) / len(payload), 3))
