from __future__ import annotations

import base64
import io
import mimetypes
from pathlib import Path

from PIL import Image


def compress_image(src: str | Path, max_side: int = 1600, quality: int = 85) -> tuple[bytes, str]:
    """Open and downscale an image, return (jpeg_bytes, mime). Used before base64."""
    im = Image.open(src)
    if im.mode not in ("RGB", "L"):
        im = im.convert("RGB")
    w, h = im.size
    longest = max(w, h)
    if longest > max_side:
        scale = max_side / longest
        im = im.resize((int(w * scale), int(h * scale)))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue(), "image/jpeg"


def image_to_data_url(path: str | Path, compress: bool = True) -> str:
    if compress:
        data, mime = compress_image(path)
    else:
        mime = mimetypes.guess_type(str(path))[0] or "image/png"
        data = Path(path).read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"
