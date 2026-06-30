from app.drive.auth import authenticate
from app.drive.scanner import connect, scan_folder
from app.database.db import create_tables


def main():

    create_tables()
    
    print("Connecting to Google Drive...")

    creds = authenticate()

    service = connect(creds)

    print("✅ Connected!\n")

    print("\nScanning Google Drive...\n")

    scan_folder(service)

    print("\nScan Complete.")


if __name__ == "__main__":
    main()
