from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ScanContext:
    started_at: datetime = field(default_factory=datetime.now)

    total_files: int = 0
    total_folders: int = 0

    saved: int = 0
    skipped: int = 0
    updated: int = 0
    deleted: int = 0

    errors: int = 0

    def finish(self):
        self.finished_at = datetime.now()

    @property
    def duration(self):
        if hasattr(self, "finished_at"):
            return self.finished_at - self.started_at
        return datetime.now() - self.started_at