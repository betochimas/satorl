from pathlib import Path

from satorl.storage.base import Storage

class LocalStorage(Storage):
    def write_text(self, content: str, destination: str) -> str:
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return str(path.resolve())
