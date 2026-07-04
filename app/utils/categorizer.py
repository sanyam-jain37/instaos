from pathlib import Path


VIDEO = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".m4v",
    ".webm"
}

IMAGE = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".heic",
    ".webp"
}

AUDIO = {
    ".mp3",
    ".wav",
    ".aac",
    ".flac",
    ".ogg"
}

DESIGN = {
    ".psd",
    ".ai",
    ".eps",
    ".svg",
    ".dxf"
}

DOCUMENT = {
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx"
}

ARCHIVE = {
    ".zip",
    ".rar",
    ".7z"
}


def categorize(name, mime):

    ext = Path(name).suffix.lower()

    if mime.startswith("video/"):
        return "VIDEO"

    if mime.startswith("image/"):
        return "IMAGE"

    if mime.startswith("audio/"):
        return "AUDIO"

    if ext in VIDEO:
        return "VIDEO"

    if ext in IMAGE:
        return "IMAGE"

    if ext in AUDIO:
        return "AUDIO"

    if ext in DESIGN:
        return "DESIGN"

    if ext in DOCUMENT:
        return "DOCUMENT"

    if ext in ARCHIVE:
        return "ARCHIVE"

    if mime.startswith("application/vnd.google-apps"):
        return "GOOGLE"

    return "OTHER"
