"""
Multipart / streaming uploads for large objects (S3 multipart API; GCS resumable upload via ``upload_from_file``).
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Any, BinaryIO, Iterator, Optional, Union

if TYPE_CHECKING:
    from .base import IStorageBackend
    from .gcs_backend import GCSStorageBackend
    from .s3_backend import S3StorageBackend


@contextmanager
def _open_path_or_stream(
    path_or_file: Union[str, Path, BinaryIO],
) -> Iterator[BinaryIO]:
    if isinstance(path_or_file, (str, Path)):
        with open(path_or_file, "rb") as f:
            yield f
    else:
        yield path_or_file


def multipart_upload_large_file(
    backend: IStorageBackend,
    key: str,
    path_or_file: Union[str, Path, BinaryIO],
    *,
    part_size: int = 8 * 1024 * 1024,
    content_type: Optional[str] = None,
    metadata: Optional[dict[str, str]] = None,
) -> str:
    """
    Upload a large object using S3 multipart (``create_multipart_upload`` / ``upload_part`` / ``complete``)
    or GCS streaming upload (``Blob.upload_from_file``, resumable for large streams).

    ``part_size`` applies to S3 only (minimum 5 MiB per part except the last; default 8 MiB).
    """
    from .gcs_backend import GCSStorageBackend
    from .s3_backend import S3StorageBackend

    if isinstance(backend, S3StorageBackend):
        return _multipart_upload_s3(
            backend,
            key,
            path_or_file,
            part_size=part_size,
            content_type=content_type,
            metadata=metadata,
        )
    if isinstance(backend, GCSStorageBackend):
        return _multipart_upload_gcs(backend, key, path_or_file, content_type=content_type)
    raise ValueError(
        f"multipart_upload_large_file supports S3 and GCS backends only; got {backend.name!r}"
    )


def _multipart_upload_s3(
    backend: S3StorageBackend,
    key: str,
    path_or_file: Union[str, Path, BinaryIO],
    *,
    part_size: int,
    content_type: Optional[str],
    metadata: Optional[dict[str, str]],
) -> str:
    k = backend._key(key)
    client = backend._client
    bucket = backend._bucket
    extra: dict[str, Any] = {}
    if content_type:
        extra["ContentType"] = content_type
    if metadata:
        extra["Metadata"] = metadata
    mpu = client.create_multipart_upload(Bucket=bucket, Key=k, **extra)
    upload_id = mpu["UploadId"]
    parts: list[dict] = []
    try:
        with _open_path_or_stream(path_or_file) as fp:
            part_number = 1
            first = True
            while True:
                chunk = fp.read(part_size)
                if not chunk:
                    if first:
                        resp = client.upload_part(
                            Bucket=bucket,
                            Key=k,
                            PartNumber=part_number,
                            UploadId=upload_id,
                            Body=b"",
                        )
                        parts.append({"ETag": resp["ETag"], "PartNumber": part_number})
                    break
                first = False
                resp = client.upload_part(
                    Bucket=bucket,
                    Key=k,
                    PartNumber=part_number,
                    UploadId=upload_id,
                    Body=chunk,
                )
                parts.append({"ETag": resp["ETag"], "PartNumber": part_number})
                part_number += 1
        if not parts:
            client.abort_multipart_upload(Bucket=bucket, Key=k, UploadId=upload_id)
            raise ValueError("nothing to upload")
        client.complete_multipart_upload(
            Bucket=bucket,
            Key=k,
            UploadId=upload_id,
            MultipartUpload={"Parts": sorted(parts, key=lambda p: p["PartNumber"])},
        )
    except Exception:
        try:
            client.abort_multipart_upload(Bucket=bucket, Key=k, UploadId=upload_id)
        except Exception:
            pass
        raise
    return f"s3://{bucket}/{k}"


def _multipart_upload_gcs(
    backend: GCSStorageBackend,
    key: str,
    path_or_file: Union[str, Path, BinaryIO],
    *,
    content_type: Optional[str],
) -> str:
    bucket = backend._client.bucket(backend._bucket_name)
    blob = bucket.blob(backend._key(key))
    with _open_path_or_stream(path_or_file) as fp:
        blob.upload_from_file(fp, content_type=content_type, rewind=True)
    return f"gs://{backend._bucket_name}/{backend._key(key)}"
