from collections import deque


class DriveIndexer:

    def __init__(self, service):
        self.service = service

    def scan(self):

        queue = deque()

        queue.append(("root", "My Drive"))

        while queue:

            folder_id, folder_path = queue.popleft()

            print(f"\n📂 Scanning: {folder_path}")

            page_token = None

            while True:

                results = (
                    self.service.files()
                    .list(
                        q=f"'{folder_id}' in parents and trashed=false",
                        fields="nextPageToken, files(id,name,mimeType,shortcutDetails)",
                        pageSize=100,
                        pageToken=page_token,
                    )
                    .execute()
                )

                files = results.get("files", [])

                for file in files:

                    name = file["name"]
                    mime = file["mimeType"]
                    file_id = file["id"]

                    print(name)

                    if mime == "application/vnd.google-apps.folder":

                        queue.append(
                            (
                                file_id,
                                f"{folder_path}/{name}",
                            )
                        )

                    elif mime == "application/vnd.google-apps.shortcut":

                        details = file.get("shortcutDetails", {})

                        target_id = details.get("targetId")

                        if target_id:

                            queue.append(
                                (
                                    target_id,
                                    f"{folder_path}/{name}",
                                )
                            )

                page_token = results.get("nextPageToken")

                if page_token is None:
                    break