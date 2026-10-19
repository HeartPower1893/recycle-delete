import ctypes
import ctypes.wintypes as w
import os
import sys

FO_DELETE = 3
FOF_SILENT = 0x0004
FOF_NOCONFIRMATION = 0x0010
FOF_ALLOWUNDO = 0x0040
FOF_NOERRORUI = 0x0400


class SHFILEOPSTRUCTW(ctypes.Structure):
    _fields_ = [
        ("hwnd", w.HWND),
        ("wFunc", w.UINT),
        ("pFrom", w.LPCWSTR),
        ("pTo", w.LPCWSTR),
        ("fFlags", ctypes.c_uint16),
        ("fAnyOperationsAborted", w.BOOL),
        ("hNameMappings", ctypes.c_void_p),
        ("lpszProgressTitle", w.LPCWSTR),
    ]


def dir_size(path):
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def recycle(path):
    if not os.path.exists(path):
        return ("MISSING", 0, 0)

    size = dir_size(path)
    buf = ctypes.create_unicode_buffer(path + "\0", len(path) + 2)
    op = SHFILEOPSTRUCTW()
    op.hwnd = None
    op.wFunc = FO_DELETE
    op.pFrom = ctypes.cast(buf, w.LPCWSTR)
    op.pTo = None
    op.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT | FOF_NOERRORUI
    op.fAnyOperationsAborted = False
    op.hNameMappings = None
    op.lpszProgressTitle = None

    res = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(op))
    aborted = bool(op.fAnyOperationsAborted)

    if res != 0:
        return ("ERROR", size, res)
    if aborted:
        return ("ABORTED", size, res)
    if os.path.exists(path):
        return ("STILL_EXISTS", size, res)
    return ("OK", size, res)


if __name__ == "__main__":
    targets = sys.argv[1:] or [
        r"C:\Users\codeg\AppData\Local\Colossal Order\Cities_Skylines",
        r"C:\Users\codeg\AppData\LocalLow\Colossal Order\Cities Skylines II",
    ]
    for t in targets:
        status, size, code = recycle(t)
        print(f"{status}\t{size / 1024 / 1024:.0f} MB\tcode={code}\t{t}", flush=True)
