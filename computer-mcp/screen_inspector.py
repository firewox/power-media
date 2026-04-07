import os
import time
import mss
import mss.tools
import easyocr
from typing import Any

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["ch_sim", "en"], gpu=False)
    return _reader


def take_screenshot(region: dict | None = None) -> dict[str, Any]:
    """
    Capture screen. region: {top, left, width, height} or None for fullscreen.
    Returns {"success": True, "path": "...", "width": N, "height": N}
    """
    os.makedirs("computer-mcp/screenshots", exist_ok=True)
    filename = f"computer-mcp/screenshots/shot_{int(time.time()*1000)}.png"
    with mss.mss() as sct:
        monitor = region if region else sct.monitors[0]
        shot = sct.grab(monitor)
        mss.tools.to_png(shot.rgb, shot.size, output=filename)
    return {
        "success": True,
        "path": filename,
        "width": shot.size[0],
        "height": shot.size[1],
    }


def inspect_screen(region: dict | None = None) -> dict[str, Any]:
    """
    Screenshot + OCR. Returns screenshot path and list of OCR text blocks.
    Each block: {"text": str, "bbox": [[x,y], ...], "confidence": float}
    """
    shot = take_screenshot(region)
    reader = _get_reader()
    raw = reader.readtext(shot["path"])
    blocks = [
        {
            "text": text,
            "bbox": bbox,
            "confidence": round(float(conf), 3),
        }
        for bbox, text, conf in raw
    ]
    return {
        "screenshot_path": shot["path"],
        "width": shot["width"],
        "height": shot["height"],
        "ocr_blocks": blocks,
    }
