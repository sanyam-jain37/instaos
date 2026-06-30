from googleapiclient.discovery import build
from app.database.db import save_reel

VIDEO_EXTENSIONS = (
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".webm",
    ".m4v",
)


def connect(creds):
    return build("drive", "v3", credentials=creds)


def scan_folder(service, folder_id="root", path="My Drive"):

    query = f"'{folder_id}' in parents and trashed=false"

    results = service.files().list(
        q=query,
        fields="files(id,name,mimeType,shortcutDetails)"
    ).execute()

    files = results.get("files", [])

    for file in files:

        name = file["name"]
        mime = file["mimeType"]
        file_id = file["id"]

        print(file)

        # ---------------------------
        # Normal Folder
        # ---------------------------
        if mime == "application/vnd.google-apps.folder":

            print(f"📁 {path}/{name}")

            scan_folder(
                service,
                file_id,
                f"{path}/{name}"
            )

        # ---------------------------
        # Shortcut
        # ---------------------------
        elif mime == "application/vnd.google-apps.shortcut":

            print(f"🔗 Shortcut: {path}/{name}")

            details = file.get("shortcutDetails")

            if details:

                target_id = details.get("targetId")
                target_mime = details.get("targetMimeType")

                print("Target:", target_id)
                print("Target Mime:", target_mime)

                if target_mime == "application/vnd.google-apps.folder":

                    scan_folder(
                        service,
                        target_id,
                        f"{path}/{name}"
                    )

        # ---------------------------
        # Video
        # ---------------------------
        else:

            if (
                mime.startswith("video/")
                or name.lower().endswith(VIDEO_EXTENSIONS)
            ):

                print(f"🎥 FOUND VIDEO: {path}/{name}")

                save_reel(
                    file_id=file_id,
                    name=name,
                    folder=path,
                    mime_type=mime,
                )