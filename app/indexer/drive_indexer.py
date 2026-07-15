from app.database.repository import FileRepository
from app.services.metadata_service import MetadataService


class DriveIndexer:
    """Incrementally index Google Drive files into the local catalog."""

    def __init__(self, service):
        self.service = service
        self.repository = FileRepository()
        # Populated once when a scan starts, then used for every file lookup.
        self.file_cache = {}

        self.total_files = 0
        self.total_folders = 0

        self.saved_files = 0
        self.updated_files = 0
        self.skipped_files = 0
        self.errors = 0

    def scan(self):
        print("\nStarting Google Drive index...\n")
        # One database read creates the cache for this complete scan.
        self.file_cache = self.repository.get_by_drive_id_map()
        print(f"Loaded {len(self.file_cache)} indexed files into memory")

        try:
            self._scan_folder(
                folder_id="root",
                current_path="My Drive",
            )
            self.repository.commit_buffer()
            self.print_summary()
        finally:
            self.repository.close()

    def _get_files(self, folder_id, page_token=None):
        return self.service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields=(
                "nextPageToken,files(id,name,mimeType,parents,size,"
                "md5Checksum,createdTime,modifiedTime,shortcutDetails)"
            ),
            pageSize=1000,
            pageToken=page_token,
        ).execute()

    def _process_item(self, item, current_path):
        mime = item["mimeType"]

        if mime == "application/vnd.google-apps.folder":
            self.total_folders += 1
            print(f"Folder: {current_path}/{item['name']}")
            self._scan_folder(item["id"], f"{current_path}/{item['name']}")
            return

        self.total_files += 1

        try:
            file = MetadataService.build_file(item, current_path)
            # All per-file existence checks stay in memory after initialization.
            existing = self.file_cache.get(file.drive_file_id)

            if existing is None:
                self.repository.add_to_buffer(file)
                self.file_cache[file.drive_file_id] = file
                self.saved_files += 1
                print(f"Saved: {file.name}")
            elif existing.modified_time == file.modified_time:
                self.skipped_files += 1
                print(f"Skipped: {file.name}")
            else:
                self.repository.update(existing, file)
                self.updated_files += 1
                print(f"Updated: {file.name}")

        except Exception as error:
            self.errors += 1
            print(f"Error: {item['name']} -> {error}")

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
            response = self._get_files(folder_id, page_token)
            files = response.get("files", [])

            print(f"\nScanning: {current_path}")
            print(f"Found {len(files)} items")

            for item in files:
                self._process_item(item, current_path)

            page_token = response.get("nextPageToken")
            if page_token is None:
                break
