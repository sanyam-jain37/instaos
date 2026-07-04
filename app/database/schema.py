from app.database.db import connect_db


def create_schema():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        drive_file_id TEXT UNIQUE NOT NULL,

        parent_drive_id TEXT,

        name TEXT NOT NULL,

        extension TEXT,

        mime_type TEXT,

        category TEXT,

        full_path TEXT,

        folder_name TEXT,

        drive_url TEXT,

        size INTEGER,

        created_time TEXT,

        modified_time TEXT,

        md5_checksum TEXT,

        is_folder INTEGER DEFAULT 0,

        is_shortcut INTEGER DEFAULT 0,

        indexed_at TEXT,

        last_scanned TEXT

    );
    """)

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_drive_file_id ON files(drive_file_id)"
    )

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_category ON files(category)"
    )

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_folder ON files(folder_name)"
    )

    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_extension ON files(extension)"
    )

    conn.commit()
    conn.close()

    print("✅ Database Ready")