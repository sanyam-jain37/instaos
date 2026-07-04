from pathlib import Path


class CategoryService:

    MIME_CATEGORY = {

        # ---------- Videos ----------
        "video/": "VIDEO",

        # ---------- Images ----------
        "image/": "IMAGE",

        # ---------- Audio ----------
        "audio/": "AUDIO",

        # ---------- PDFs ----------
        "application/pdf": "PDF",

        # ---------- Google Workspace ----------
        "application/vnd.google-apps.document": "DOCUMENT",
        "application/vnd.google-apps.spreadsheet": "SPREADSHEET",
        "application/vnd.google-apps.presentation": "PRESENTATION",
        "application/vnd.google-apps.form": "FORM",
        "application/vnd.google-apps.folder": "FOLDER",
        "application/vnd.google-apps.shortcut": "SHORTCUT",
        "application/vnd.google-apps.drawing": "DRAWING",

        # ---------- Archives ----------
        "application/zip": "ARCHIVE",
        "application/x-zip-compressed": "ARCHIVE",
        "application/x-rar-compressed": "ARCHIVE",
        "application/x-7z-compressed": "ARCHIVE",
        "application/x-tar": "ARCHIVE",

        # ---------- Design ----------
        "application/vnd.adobe.photoshop": "DESIGN",
        "application/postscript": "VECTOR",
        "image/svg+xml": "VECTOR",

        # ---------- Code ----------
        "text/x-python": "CODE",
        "text/x-csrc": "CODE",
        "text/x-c++src": "CODE",
        "application/javascript": "CODE",
        "text/html": "CODE",
        "application/json": "CODE",

        # ---------- Documents ----------
        "application/msword": "DOCUMENT",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCUMENT",
        "application/vnd.ms-excel": "SPREADSHEET",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "SPREADSHEET",
        "application/vnd.ms-powerpoint": "PRESENTATION",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PRESENTATION",
    }

    EXTENSION_CATEGORY = {

        ".mp4": "VIDEO",
        ".mov": "VIDEO",
        ".avi": "VIDEO",
        ".mkv": "VIDEO",
        ".webm": "VIDEO",
        ".m4v": "VIDEO",

        ".jpg": "IMAGE",
        ".jpeg": "IMAGE",
        ".png": "IMAGE",
        ".gif": "IMAGE",
        ".webp": "IMAGE",
        ".heic": "IMAGE",

        ".mp3": "AUDIO",
        ".wav": "AUDIO",
        ".aac": "AUDIO",
        ".ogg": "AUDIO",

        ".pdf": "PDF",

        ".zip": "ARCHIVE",
        ".rar": "ARCHIVE",
        ".7z": "ARCHIVE",

        ".psd": "DESIGN",
        ".ai": "VECTOR",
        ".eps": "VECTOR",
        ".svg": "VECTOR",

        ".py": "CODE",
        ".cpp": "CODE",
        ".c": "CODE",
        ".js": "CODE",
        ".ts": "CODE",
        ".java": "CODE",

        ".docx": "DOCUMENT",
        ".doc": "DOCUMENT",

        ".xlsx": "SPREADSHEET",
        ".xls": "SPREADSHEET",

        ".pptx": "PRESENTATION",
        ".ppt": "PRESENTATION",
    }

    @classmethod
    def get_category(cls, mime_type: str, filename: str) -> str:

        # Exact MIME match
        if mime_type in cls.MIME_CATEGORY:
            return cls.MIME_CATEGORY[mime_type]

        # MIME prefix match
        for prefix, category in cls.MIME_CATEGORY.items():
            if prefix.endswith("/") and mime_type.startswith(prefix):
                return category

        # Extension fallback
        extension = Path(filename).suffix.lower()

        if extension in cls.EXTENSION_CATEGORY:
            return cls.EXTENSION_CATEGORY[extension]

        return "OTHER"