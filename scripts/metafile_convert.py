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


def metafile_or_raster_to_png(data: bytes, ext: str, out_path: str):
    """Dispatches by source extension: .wmf/.emf go through GDI; anything
    else (png/jpg/gif/bmp -- a small number of the report's images are
    already raster, e.g. photographs used in question stimulus) is a
    straight Pillow passthrough/re-encode to PNG. Returns (width, height)."""
    ext = ext.lower().lstrip(".")
    if ext == "wmf":
        return wmf_to_png(data, out_path)
    if ext == "emf":
        return emf_to_png(data, out_path)
    from io import BytesIO

    im = Image.open(BytesIO(data)).convert("RGB")
    im.save(out_path)
    return im.size
