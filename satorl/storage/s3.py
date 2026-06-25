from urllib.parse import urlparse

import boto3

from satorl.storage.base import Storage

class S3Storage(Storage):
    def __init__(self, client=None) -> None:
        # injectable client -> trivial to mock in tests (e.g. moto)
        self._client = client or boto3.client("s3")

    def write_text(self, content: str, destination: str) -> str:
        bucket, key = _parse_s3_uri(destination)
        self._client.put_object(Bucket=bucket, Key=key, Body=content)
        return destination

def _parse_s3_uri(uri: str) -> tuple[str, str]:
    parsed = urlparse(uri)
    bucket, key = parsed.netloc, parsed.path.lstrip("/")
    if not bucket or not key:
        raise ValueError(f"Invalid S3 URI {uri!r} (expected s3://bucket/key)")
    return bucket, key