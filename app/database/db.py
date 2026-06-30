import sqlite3
from pathlib import Path

DB_PATH = Path("data/reels.db")


def connect_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reels(
            id TEXT PRIMARY KEY,
            name TEXT,
            folder TEXT,
            mime_type TEXT,
            drive_link TEXT,
            caption TEXT,
            hashtags TEXT,
            posted INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

    print("✅ Database Ready")


def save_reel(file_id, name, folder, mime_type):
    conn = connect_db()
    cursor = conn.cursor()

    drive_link = f"https://drive.google.com/file/d/{file_id}/view"

    cursor.execute("""
        INSERT OR IGNORE INTO reels
        (id, name, folder, mime_type, drive_link)
        VALUES (?, ?, ?, ?, ?)
    """, (
        file_id,
        name,
        folder,
        mime_type,
        drive_link
    ))

    conn.commit()
    conn.close()