from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile

UPLOADS_DIR = Path(__file__).resolve().parents[2] / "uploads"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
ALLOWED_TYPES = {
    "image/jpeg": (".jpg", lambda data: data.startswith(b"\xff\xd8\xff")),
    "image/png": (".png", lambda data: data.startswith(b"\x89PNG\r\n\x1a\n")),
    "image/webp": (".webp", lambda data: len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"),
}


async def save_image(upload: UploadFile) -> str:
    mime_type = (upload.content_type or "").lower()
    kind = ALLOWED_TYPES.get(mime_type)
    if kind is None:
        raise HTTPException(status_code=415, detail="Upload must be a JPG, PNG, or WebP image")
    data = await upload.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image must be 5 MB or smaller")
    extension, signature_check = kind
    if not signature_check(data):
        raise HTTPException(status_code=415, detail="Uploaded file content does not match its image type")
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    (UPLOADS_DIR / filename).write_bytes(data)
    return f"/uploads/{filename}"
