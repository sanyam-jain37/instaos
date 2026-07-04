from app.database.database import create_database
from app.drive.auth import authenticate
from app.drive.scanner import connect
from app.indexer.drive_indexer import DriveIndexer


def main():
    print("=" * 50)
    print("🚀 InstaOS Starting...")
    print("=" * 50)

    # Create database tables
    create_database()

    print("🔐 Authenticating with Google Drive...")
    creds = authenticate()

    print("🔗 Connecting to Google Drive...")
    service = connect(creds)

    print("✅ Connected!")

    print("\n📂 Starting Indexer...\n")

    indexer = DriveIndexer(service)
    indexer.scan()

    print("\n🎉 Scan Finished Successfully!")


if __name__ == "__main__":
    main()