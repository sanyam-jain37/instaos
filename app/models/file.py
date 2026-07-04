from dataclasses import dataclass


@dataclass
class DriveFile:

    id: str
    name: str
    mime: str

    extension: str

    parent: str

    full_path: str

    category: str

    size: int = 0

    created: str = ""

    modified: str = ""

    web_link: str = ""