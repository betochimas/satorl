from urllib.parse import urlparse

from satorl.storage.base import Storage
from satorl.storage.local import LocalStorage
from satorl.storage.s3 import S3Storage

def open_destination(uri: str) -> Storage:
    """Pick a storage backend from the destination URI's scheme."""
    scheme = urlparse(uri).scheme
    if scheme == "s3":
        return S3Storage()
    if scheme in ("", "file"):
        return LocalStorage()
    raise ValueError(f"Unsupported storage backend {scheme!r} in {uri!r}")