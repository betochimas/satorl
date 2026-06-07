import io
from urllib.parse import urlparse

import boto3
import pandas as pd

from satorl.storage.base import Storage

class S3Storage(Storage):
    def __init__(self, client=None) -> None:
        # injectable client -> trivial to mock in tests (e.g. moto)
        self._client = client or boto3.client("s3")

    def write(self, df: pd.DataFrame, destination: str) -> str:
        bucket, key = _parse_s3_uri(destination)
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        self._client.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())
        return destination

def _parse_s3_uri(uri: str) -> tuple[str, str]:
    parsed = urlparse(uri)
    bucket, key = parsed.netloc, parsed.path.lstrip("/")
    if not bucket or not key:
        raise ValueError(f"Invalid S3 URI {uri!r} (expected s3://bucket/key)")
    return bucket, key