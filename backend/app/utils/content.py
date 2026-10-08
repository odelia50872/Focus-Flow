import re
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException, status

SUPPORTED_TYPES = {"youtube", "text", "web"}

YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def parse_youtube_id(source: str) -> str:
    raw = source.strip()
    if YOUTUBE_ID_RE.match(raw):
        return raw

    if "youtu.be/" in raw:
        path = urlparse(raw).path.strip("/")
        candidate = path.split("/")[0]
        if YOUTUBE_ID_RE.match(candidate):
            return candidate

    parsed = urlparse(raw)
    if parsed.netloc.endswith("youtube.com") or parsed.netloc.endswith("youtube-nocookie.com"):
        query_id = parse_qs(parsed.query).get("v", [None])[0]
        if query_id and YOUTUBE_ID_RE.match(query_id):
            return query_id
        parts = [p for p in parsed.path.split("/") if p]
        if parts and parts[0] in {"embed", "shorts", "live"} and len(parts) > 1 and YOUTUBE_ID_RE.match(parts[1]):
            return parts[1]

    raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid YouTube link or id")


def validate_content(content_type: str, source: str) -> tuple[str, str, str | None]:
    kind = content_type.strip().lower()
    text = source.strip()
    if kind not in SUPPORTED_TYPES:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unsupported content type")
    if not text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="source is required")

    youtube_id = None
    if kind == "youtube":
        youtube_id = parse_youtube_id(text)
        text = f"https://www.youtube.com/watch?v={youtube_id}"
    elif kind == "web":
        parsed = urlparse(text)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid web URL")
    elif kind == "text" and len(text) < 20:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Text content must be at least 20 characters",
        )
    return kind, text, youtube_id
