# -*- coding: utf-8 -*-
"""
一键刷回真 MF-INK V1.0.4
自动探测当前插着的 ESP32-C3 串口 -> 擦除 -> 写入 -> 校验。
用法：
    python flash_mfink.py            # 正常刷机
    python flash_mfink.py --check    # 只检测，不刷（看板子/固件/工具是否就绪）
    python flash_mfink.py --install-bat  # 生成桌面双击启动器
"""
import sys
import os
import subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FW = os.path.join(ROOT, "firmware", "mfink_V1.0.4_merged.bin")

ESPTOOL_CANDIDATES = [
    r"C:\Espressif\python_env\idf5.5_py3.11_env\Scripts\esptool.exe",
    r"C:\Espressif\python_env\idf5.5_py3.11_env\Scripts\esptool.py",
]


def find_esptool():
    for p in ESPTOOL_CANDIDATES:
        if os.path.isfile(p):
            return p
    return None


def find_board_port():
    """返回当前真正能打开的 Espressif(VID 303A) 串口列表。幽灵设备打不开，会被自动排除。"""
    try:
        import serial
        from serial.tools import list_ports
    except Exception as e:
        print("[错误] 缺少 pyserial，无法自动探测串口: %s" % e)
        return []

    cands = []
    for info in list_ports.comports():
        if info.vid == 0x303A:  # Espressif
            cands.append(info.device)
    # 兜底：也扫一遍常见口（某些驱动不报 VID）
    for i in range(1, 41):
        name = "COM%d" % i
        if name not in cands:
            cands.append(name)

    usable = []
    for p in cands:
        try:
            s = serial.Serial(p, 115200, timeout=0.2)
            s.close()
            usable.append(p)
        except Exception:
            pass
    return usable


def run(cmd):
    # 捕获字节再手动解码，避免子进程非 UTF-8 输出在子线程里抛 UnicodeDecodeError
    p = subprocess.run(cmd, capture_output=True)
    out = p.stdout.decode("utf-8", "replace") + p.stderr.decode("utf-8", "replace")
    print(out, end="")
    return p.returncode, out


def install_bat():
    py = r"C:/Users/fqyy3/.workbuddy/binaries/python/versions/3.13.12/python.exe"
    script = (HERE + "/flash_mfink.py").replace("\\", "/")
    lines = [
        "@echo off",
        "chcp 936 >nul",
        "title MF-INK Flash",
        "echo.",
        "echo  ============================================",
        "echo   MF-INK V1.0.4  yi jian shua ji",
        "echo  ============================================",
        "echo.",
        "echo   Qing ba banzi USB cha hao, ran hou an ren yi jian kai shi...",
        "pause >nul",
        "echo.",
        '"%s" "%s"' % (py, script),
        "echo.",
        "echo  Sha ji jie shu, an ren yi jian guan bi chuang kou.",
        "pause >nul",
    ]
    # .bat 必须 GBK 编码 + CRLF 换行（本机 cmd 码页 936）
    data = "\r\n".join(lines).encode("gbk")
    targets = [
        os.path.join(ROOT, "一键刷MF-INK.bat"),
        r"C:\Users\fqyy3\Desktop\一键刷MF-INK.bat",
    ]
    for path in targets:
        with open(path, "wb") as f:
            f.write(data)
        print("已生成: %s" % path)


def main():
    print("=" * 56)
    print(" MF-INK V1.0.4  yi jian shua ji")
    print("=" * 56)

    if not os.path.isfile(FW):
        print("[错误] 找不到固件: %s" % FW)
        return 2
    esp = find_esptool()
    if not esp:
        print("[错误] 找不到 esptool.exe")
        return 2

    print("固件: %s" % FW)
    print("工具: %s" % esp)
    print()
    # 支持手动指定端口：python flash_mfink.py --port COM29
    manual_port = None
    if "--port" in sys.argv:
        idx = sys.argv.index("--port")
        if idx + 1 < len(sys.argv):
            manual_port = sys.argv[idx + 1].upper()

    print("正在检测板子串口...")
    ports = find_board_port()
    if manual_port:
        port = manual_port
        print("使用指定端口: %s" % port)
    elif not ports:
        print("[提示] 没找到插着的板子串口（这是正常保护，不是脚本坏了）。")
        print("       常见原因：USB 线松了 / 板子没上电 / 端口还没就绪。")
        print("       处理：重新插一下 USB 线，等 2 秒，再双击一次。")
        print("       如果插好了还不行，在命令行用 --port COMxx 手动指定。")
        return 1
    else:
        port = ports[0]
        if len(ports) > 1:
            print("检测到多个可用串口: %s" % ", ".join(ports))
            print("默认使用第一个: %s" % port)
        else:
            print("检测到板子: %s" % port)

    if "--check" in sys.argv:
        print("\n[--check] 只检测，不刷机。就绪。")
        return 0

    print()
    print(">>> 步骤 1/2: 擦除 flash")
    rc, out = run([esp, "--port", port, "--baud", "460800", "erase_flash"])
    if rc != 0 or "successfully" not in out.lower():
        print("[错误] 擦除失败，未写入。")
        return 1

    print(">>> 步骤 2/2: 写入固件并校验")
    rc, out = run([esp, "--port", port, "--baud", "460800", "write_flash", "--verify", "0x0", FW])
    if rc != 0 or "Hash of data verified" not in out:
        print("[错误] 写入或校验失败。")
        return 1

    print("=" * 56)
    print(" 刷机完成！")
    print(" 接下来：")
    print("   1. 手机/电脑连热点 MF-INK-XXXX")
    print("   2. 浏览器打开 192.168.4.1")
    print("   3. 网页里上传图片推图")
    print("=" * 56)
    return 0


if __name__ == "__main__":
    if "--install-bat" in sys.argv:
        install_bat()
        sys.exit(0)
    sys.exit(main())
