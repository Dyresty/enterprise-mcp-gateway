from datetime import datetime, timezone
from pathlib import Path

from app.config import settings

TEXT_EXTENSIONS = {".md", ".txt", ".csv", ".json", ".yaml", ".yml", ".py", ".sql", ".log"}
MAX_READ_BYTES = 200_000
MAX_SEARCH_RESULTS = 50


class FileAccessError(ValueError):
    """Raised for paths outside the sandbox, unsupported file types or oversized files."""


class FileSystemClient:
    """
    Read-only access to one sandbox folder. Every path is resolved
    (including symlinks) and must stay inside the root.
    """

    def __init__(self, root: str | None = None):
        self.root = Path(root or settings.FILES_ROOT).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relative_path: str) -> Path:
        candidate = (self.root / relative_path).resolve()

        if candidate != self.root and not candidate.is_relative_to(self.root):
            raise FileAccessError(f"Path '{relative_path}' is outside the allowed folder.")

        return candidate

    def list_files(self, path: str = ".", pattern: str = "*") -> list[dict]:
        folder = self.resolve(path)

        if not folder.is_dir():
            raise FileAccessError(f"'{path}' is not a folder.")

        entries = []
        for item in sorted(folder.glob(pattern)):
            # glob can follow symlinks; re-check every result against the sandbox
            if not item.resolve().is_relative_to(self.root):
                continue
            stat = item.stat()
            entries.append(
                {
                    "path": item.relative_to(self.root).as_posix(),
                    "type": "folder" if item.is_dir() else "file",
                    "size_bytes": stat.st_size if item.is_file() else None,
                    "modified": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                }
            )
        return entries

    def read_file(self, path: str) -> dict:
        file = self.resolve(path)

        if not file.is_file():
            raise FileAccessError(f"'{path}' is not a file.")
        if file.suffix.lower() not in TEXT_EXTENSIONS:
            raise FileAccessError(f"File type '{file.suffix}' is not allowed.")
        if file.stat().st_size > MAX_READ_BYTES:
            raise FileAccessError(f"'{path}' is larger than {MAX_READ_BYTES} bytes.")

        return {
            "path": file.relative_to(self.root).as_posix(),
            "content": file.read_text(encoding="utf-8", errors="replace"),
        }

    def search_files(self, query: str, path: str = ".") -> list[dict]:
        """Case-insensitive text search over allowed files; returns matching lines."""
        folder = self.resolve(path)
        needle = query.lower()
        matches = []

        for file in sorted(folder.rglob("*")):
            if (
                not file.is_file()
                or file.suffix.lower() not in TEXT_EXTENSIONS
                or not file.resolve().is_relative_to(self.root)
                or file.stat().st_size > MAX_READ_BYTES
            ):
                continue

            lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
            for number, line in enumerate(lines, start=1):
                if needle in line.lower():
                    matches.append(
                        {
                            "path": file.relative_to(self.root).as_posix(),
                            "line": number,
                            "text": line.strip()[:300],
                        }
                    )
                    if len(matches) >= MAX_SEARCH_RESULTS:
                        return matches
        return matches
