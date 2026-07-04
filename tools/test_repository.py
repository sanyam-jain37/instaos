from app.database.database import create_database
from app.database.models import File
from app.database.repository import FileRepository


def main():
    create_database()

    repo = FileRepository()

    test_file = File(
        drive_file_id="TEST123",
        parent_drive_id="ROOT",
        name="demo.mp4",
        extension=".mp4",
        mime_type="video/mp4",
        category="VIDEO",
        full_path="My Drive/Test/demo.mp4",
        folder_name="Test",
        drive_url="https://drive.google.com",
        size=123456,
        is_folder=False,
        is_shortcut=False,
    )

    repo.add(test_file)

    files = repo.get_all()

    print("\nFILES IN DATABASE\n")

    for f in files:
        print(
            f.id,
            f.name,
            f.category,
            f.mime_type,
        )

    repo.close()


if __name__ == "__main__":
    main()