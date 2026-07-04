from app.services.category_service import CategoryService

tests = [
    ("video/mp4", "reel.mp4"),
    ("image/jpeg", "photo.jpg"),
    ("audio/mpeg", "song.mp3"),
    ("application/pdf", "ebook.pdf"),
    ("application/vnd.google-apps.document", "Notes"),
    ("application/postscript", "logo.ai"),
    ("application/octet-stream", "unknown.xyz"),
]

for mime, name in tests:
    print(f"{name} -> {CategoryService.get_category(mime, name)}")