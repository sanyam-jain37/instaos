from app.database.repository import FileRepository
from app.services.metadata_service import MetadataService


class DriveIndexer:

    def __init__(self, service):
        self.service = service
        self.repository = FileRepository()

        self.total_files = 0
        self.total_folders = 0

        self.saved_files = 0
        self.updated_files = 0
        self.skipped_files = 0
        self.errors = 0

    def scan(self):

        print("\n🚀 Starting Google Drive Index...\n")

        self._scan_folder(
            folder_id="root",
            current_path="My Drive",
        )

        self.print_summary()
        self.repository.close()

    def _get_files(self, folder_id, page_token=None):

        return self.service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken,files(id,name,mimeType,parents,size,md5Checksum,createdTime,modifiedTime,shortcutDetails)",
            pageSize=1000,
            pageToken=page_token,
        ).execute()

    def _process_item(self, item, current_path):

        mime = item["mimeType"]

        if mime == "application/vnd.google-apps.folder":

            self.total_folders += 1

            print(f"📁 {current_path}/{item['name']}")

            self._scan_folder(
                item["id"],
                f"{current_path}/{item['name']}"
            )

            return

        self.total_files += 1

        try:

            file = MetadataService.build_file(
                item,
                current_path,
            )

            existing = self.repository.get_by_drive_id(
                file.drive_file_id
            )

            if existing is None:

                self.repository.add(file)

                self.saved_files += 1
                print(f"✅ Saved: {file.name}")

            else:

                print("\n==========================")
                print("FILE :", file.name)
                print("DB   :", existing.modified_time, type(existing.modified_time))
                print("NEW  :", file.modified_time, type(file.modified_time))
                print("EQUAL:", existing.modified_time == file.modified_time)
                print("==========================")

                if existing.modified_time == file.modified_time:

                    self.skipped_files += 1
                    print(f"⏩ Skipped: {file.name}")

                else:

                    self.repository.update(
                        existing,
                        file,
                    )

                    self.updated_files += 1
                    print(f"🔄 Updated: {file.name}")

        except Exception as e:

            self.errors += 1
            print(f"❌ {item['name']} -> {e}")

    def print_summary(self):

        print("\n" + "=" * 45)
        print("INDEX COMPLETE")
        print("=" * 45)
        print(f"Folders : {self.total_folders}")
        print(f"Files   : {self.total_files}")
        print(f"Saved   : {self.saved_files}")
        print(f"Updated : {self.updated_files}")
        print(f"Skipped : {self.skipped_files}")
        print(f"Errors  : {self.errors}")
        print("=" * 45)

    def _scan_folder(self, folder_id, current_path):

        page_token = None

        while True:

            response = self._get_files(
                folder_id,
                page_token,
            )

            files = response.get("files", [])

            print(f"\n📂 Scanning: {current_path}")
            print(f"Found {len(files)} items")

            for item in files:
                self._process_item(
                    item,
                    current_path,
                )

            page_token = response.get("nextPageToken")

            if page_token is None:
                break
