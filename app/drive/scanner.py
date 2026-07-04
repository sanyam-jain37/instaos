from googleapiclient.discovery import build


def connect(creds):
    """
    Create and return a Google Drive service.
    """
    return build(
        "drive",
        "v3",
        credentials=creds,
    )