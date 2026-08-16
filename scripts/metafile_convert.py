"""Converts Windows Metafile (WMF) and Enhanced Metafile (EMF) images to PNG
using the native Windows GDI metafile player, via ctypes -- Windows-only,
which is fine: this is a one-time, developer-machine extraction step, not
something that needs to run in the deployed app or CI.

Why this exists: VCAA's examination reports embed worked equations as Word
"Equation Editor"/MathType OLE objects, whose on-screen preview is a WMF (or
occasionally EMF) image (confirmed directly in the 2025 VCE Physics report's
own XML: 111 embedded WMF images across 35 Section B subquestions, plus 7
Section A comment cells). Pillow's own WMF reader does not implement a real
metafile interpreter and renders these badly -- confirmed by direct
comparison: Pillow produces garbled, overlapping glyphs ("T=760N" rendered
as illegible overlapping strokes) for the exact same file GDI renders
correctly ("T = 760 N", crisp). Since these images are the actual worked
solution content, not decorative, correctness here matters more than
portability.
"""
import ctypes
import struct
from ctypes import wintypes

from PIL import Image

gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
user32 = ctypes.WinDLL("user32", use_last_error=True)

gdi32.SetMetaFileBitsEx.restype = wintypes.HANDLE
gdi32.SetMetaFileBitsEx.argtypes = [wintypes.UINT, ctypes.c_char_p]
gdi32.PlayMetaFile.restype = wintypes.BOOL
gdi32.PlayMetaFile.argtypes = [wintypes.HDC, wintypes.HANDLE]
gdi32.DeleteMetaFile.restype = wintypes.BOOL
gdi32.DeleteMetaFile.argtypes = [wintypes.HANDLE]

gdi32.SetEnhMetaFileBits.restype = wintypes.HANDLE
gdi32.SetEnhMetaFileBits.argtypes = [wintypes.UINT, ctypes.c_char_p]
gdi32.PlayEnhMetaFile.restype = wintypes.BOOL
gdi32.PlayEnhMetaFile.argtypes = [wintypes.HDC, wintypes.HANDLE, ctypes.c_void_p]
gdi32.DeleteEnhMetaFile.restype = wintypes.BOOL
gdi32.DeleteEnhMetaFile.argtypes = [wintypes.HANDLE]
gdi32.GetEnhMetaFileHeader.argtypes = [wintypes.HANDLE, wintypes.UINT, ctypes.c_void_p]

# Every one of these returns or accepts an HDC/HGDIOBJ/HBITMAP handle. GDI
# handles are documented by Microsoft to always fit in 32 bits even on
# 64-bit Windows, but the *pointer-sized register* these functions actually
# return can still have non-zero garbage in its upper 32 bits (or a
# genuine, harmless sign-extension of a negative-looking 32-bit handle
# value -- both observed directly on real handles from this exact code
# path). Left undeclared, ctypes defaults to a 32-bit c_int for both
# argument marshaling and return values, which is a silent, size-dependent
# truncation: it works by coincidence whenever a handle's bit pattern is
# small, and produces a corrupted, unusable handle for any other page --
# confirmed as the root cause of a real "PlayEnhMetaFile failed, err=1"
# on 2022's report (a legitimately-created, non-null metafile handle simply
# never reached PlayEnhMetaFile intact). Declaring every one of these as
# pointer-sized (HDC/HGDIOBJ, both c_void_p-compatible) makes the handle
# round-trip exact regardless of what bit pattern Windows happens to hand
# back, rather than "usually working."
HGDIOBJ = ctypes.c_void_p
user32.GetDC.restype = wintypes.HDC
user32.GetDC.argtypes = [wintypes.HWND]
user32.ReleaseDC.restype = ctypes.c_int
user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
gdi32.CreateCompatibleDC.restype = wintypes.HDC
gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
gdi32.CreateCompatibleBitmap.restype = HGDIOBJ
gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
gdi32.SelectObject.restype = HGDIOBJ
gdi32.SelectObject.argtypes = [wintypes.HDC, HGDIOBJ]
gdi32.GetStockObject.restype = HGDIOBJ
gdi32.GetStockObject.argtypes = [ctypes.c_int]
gdi32.PatBlt.restype = wintypes.BOOL
gdi32.PatBlt.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.DWORD]
gdi32.DeleteObject.restype = wintypes.BOOL
gdi32.DeleteObject.argtypes = [HGDIOBJ]
gdi32.DeleteDC.restype = wintypes.BOOL
gdi32.DeleteDC.argtypes = [wintypes.HDC]
gdi32.GetDIBits.restype = ctypes.c_int
gdi32.GetDIBits.argtypes = [wintypes.HDC, HGDIOBJ, wintypes.UINT, wintypes.UINT, ctypes.c_void_p, ctypes.c_void_p, wintypes.UINT]
gdi32.SetMapMode.restype = ctypes.c_int
gdi32.SetMapMode.argtypes = [wintypes.HDC, ctypes.c_int]
gdi32.SetWindowOrgEx.restype = wintypes.BOOL
gdi32.SetWindowOrgEx.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
gdi32.SetWindowExtEx.restype = wintypes.BOOL
gdi32.SetWindowExtEx.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
gdi32.SetViewportOrgEx.restype = wintypes.BOOL
gdi32.SetViewportOrgEx.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
gdi32.SetViewportExtEx.restype = wintypes.BOOL
gdi32.SetViewportExtEx.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]


class RECT(ctypes.Structure):
    _fields_ = [("left", wintypes.LONG), ("top", wintypes.LONG), ("right", wintypes.LONG), ("bottom", wintypes.LONG)]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG), ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD), ("biBitCount", wintypes.WORD), ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD), ("biXPelsPerMeter", wintypes.LONG), ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD), ("biClrImportant", wintypes.DWORD),
    ]


MM_ANISOTROPIC = 8
PATCOPY = 0x00F00021
WHITE_BRUSH = 0
# A little headroom beyond the metafile's own bounding box -- some OLE
# equation previews clip descenders/overlines right at the edge otherwise.
_MARGIN_UNITS = 20


def _blank_bitmap_dc(px_w, px_h):
    hdc_screen = user32.GetDC(0)
    hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
    hbmp = gdi32.CreateCompatibleBitmap(hdc_screen, px_w, px_h)
    gdi32.SelectObject(hdc_mem, hbmp)
    gdi32.SelectObject(hdc_mem, gdi32.GetStockObject(WHITE_BRUSH))
    gdi32.PatBlt(hdc_mem, 0, 0, px_w, px_h, PATCOPY)
    return hdc_screen, hdc_mem, hbmp


def _bitmap_to_png(hdc_mem, hbmp, px_w, px_h, out_path):
    bmi = BITMAPINFOHEADER()
    bmi.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.biWidth = px_w
    bmi.biHeight = -px_h  # negative = top-down DIB, matches how we drew it
    bmi.biPlanes = 1
    bmi.biBitCount = 32
    bmi.biCompression = 0  # BI_RGB
    buf = ctypes.create_string_buffer(px_w * px_h * 4)
    gdi32.GetDIBits(hdc_mem, hbmp, 0, px_h, buf, ctypes.byref(bmi), 0)
    im = Image.frombuffer("RGB", (px_w, px_h), buf.raw, "raw", "BGRX", 0, 1)
    im.save(out_path)
    return im.size


def wmf_to_png(data: bytes, out_path: str, scale: int = 8):
    """`data` is the raw bytes of a .wmf file (placeable-header WMF, the
    form Word embeds, or a bare WMF record stream). `scale` controls output
    resolution -- WMF/twip units are tiny, so this is upscaled well past
    1:1 for a crisp inline image at normal reading size."""
    if data[:4] == bytes.fromhex("d7cdc69a"):
        left, top, right, bottom = struct.unpack("<hhhh", data[6:14])
        wmf_data = data[22:]
    else:
        left, top, right, bottom = 0, 0, 2000, 500
        wmf_data = data

    width_units = max(1, right - left) + _MARGIN_UNITS
    height_units = max(1, bottom - top) + _MARGIN_UNITS
    px_w = max(1, int(width_units * scale / 20))
    px_h = max(1, int(height_units * scale / 20))

    hmf = gdi32.SetMetaFileBitsEx(len(wmf_data), wmf_data)
    if not hmf:
        raise RuntimeError(f"SetMetaFileBitsEx failed, err={ctypes.get_last_error()}")

    hdc_screen, hdc_mem, hbmp = _blank_bitmap_dc(px_w, px_h)
    try:
        gdi32.SetMapMode(hdc_mem, MM_ANISOTROPIC)
        gdi32.SetWindowOrgEx(hdc_mem, left, top, None)
        gdi32.SetWindowExtEx(hdc_mem, width_units, height_units, None)
        gdi32.SetViewportOrgEx(hdc_mem, _MARGIN_UNITS * scale // 40, _MARGIN_UNITS * scale // 40, None)
        gdi32.SetViewportExtEx(hdc_mem, px_w, px_h, None)
        if not gdi32.PlayMetaFile(hdc_mem, hmf):
            raise RuntimeError(f"PlayMetaFile failed, err={ctypes.get_last_error()}")
        size = _bitmap_to_png(hdc_mem, hbmp, px_w, px_h, out_path)
    finally:
        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(0, hdc_screen)
        gdi32.DeleteMetaFile(hmf)
    return size


def emf_to_png(data: bytes, out_path: str, scale: int = 4):
    """EMF uses device-independent (0.01 mm) units and its own GDI calls --
    not yet exercised against a real VCAA report sample (none of the years
    inspected so far use EMF for equation previews, only WMF), but
    implemented defensively since Office can choose either depending on
    version. If a future year's report includes one and this needs fixing,
    check the frame/scale math here first."""
    hemf = gdi32.SetEnhMetaFileBits(len(data), data)
    if not hemf:
        raise RuntimeError(f"SetEnhMetaFileBits failed, err={ctypes.get_last_error()}")

    header = ctypes.create_string_buffer(88)
    gdi32.GetEnhMetaFileHeader(hemf, 88, ctypes.byref(header))
    # ENHMETAHEADER.rclFrame is at offset 24, four LONGs, in .01mm units.
    frame = struct.unpack_from("<4l", header.raw, 24)
    width_mm = (frame[2] - frame[0]) / 100.0
    height_mm = (frame[3] - frame[1]) / 100.0
    px_w = max(1, int(width_mm * scale * 10))
    px_h = max(1, int(height_mm * scale * 10))

    hdc_screen, hdc_mem, hbmp = _blank_bitmap_dc(px_w, px_h)
    try:
        rect = RECT(0, 0, px_w, px_h)
        if not gdi32.PlayEnhMetaFile(hdc_mem, hemf, ctypes.byref(rect)):
            raise RuntimeError(f"PlayEnhMetaFile failed, err={ctypes.get_last_error()}")
        size = _bitmap_to_png(hdc_mem, hbmp, px_w, px_h, out_path)
    finally:
        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(0, hdc_screen)
        gdi32.DeleteEnhMetaFile(hemf)
    return size


def _emf_via_pillow(data: bytes, out_path: str, scale: int = 3):
    """Pillow's WMF reader is the broken one (see module docstring) -- its
    EMF reader is a different code path and, confirmed by direct visual
    comparison against this exact file, renders cleanly: crisp text and
    ruled table borders, not the garbled overlapping glyphs WMF produces.

    Encountering a real EMF equation preview for the first time (2022's
    report; every year inspected before it used WMF exclusively) surfaced a
    second, unrelated problem in the GDI ctypes path below: PlayEnhMetaFile
    reliably failed on every one of that year's EMF images even after
    fixing a genuine handle-truncation bug in this module's Win32
    declarations (see the HGDIOBJ comment above) -- a plain
    SetEnhMetaFileBits -> PlayEnhMetaFile round trip could not get past a
    further failure this investigation didn't chase down, since Pillow
    already solves EMF correctly with far less code. EMF is routed through
    it instead of emf_to_png below; that function is kept for reference/
    future debugging rather than deleted, but is no longer called."""
    from io import BytesIO

    im = Image.open(BytesIO(data)).convert("RGB")
    im = im.resize((max(1, im.width * scale), max(1, im.height * scale)), Image.LANCZOS)
    im.save(out_path)
    return im.size


def metafile_or_raster_to_png(data: bytes, ext: str, out_path: str):
    """Dispatches by source extension: .wmf through the native GDI player,
    .emf through Pillow (see _emf_via_pillow), anything else (png/jpg/gif/
    bmp -- a small number of the report's images are already raster, e.g.
    photographs used in question stimulus) a straight Pillow passthrough/
    re-encode to PNG. Returns (width, height)."""
    ext = ext.lower().lstrip(".")
    if ext == "wmf":
        return wmf_to_png(data, out_path)
    if ext == "emf":
        return _emf_via_pillow(data, out_path)
    from io import BytesIO

    im = Image.open(BytesIO(data)).convert("RGB")
    im.save(out_path)
    return im.size
