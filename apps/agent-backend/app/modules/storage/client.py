import uuid
from functools import lru_cache

import boto3

from app.core.config import get_settings

settings = get_settings()


@lru_cache
def get_s3_resource():
    return boto3.resource(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )


def ensure_bucket() -> None:
    client = get_s3_resource().meta.client
    existing = {b["Name"] for b in client.list_buckets()["Buckets"]}
    if settings.s3_bucket not in existing:
        client.create_bucket(Bucket=settings.s3_bucket)


def make_key(filename: str) -> str:
    """Generate a unique object key without touching the store.

    Lets the API layer reserve a key synchronously (fast) and hand the actual
    upload of the bytes off to the worker via ``put_bytes``.
    """
    return f"{uuid.uuid4()}-{filename}"


def put_bytes(key: str, file_bytes: bytes, content_type: str | None) -> None:
    extra_args = {"ContentType": content_type} if content_type else {}
    get_s3_resource().Bucket(settings.s3_bucket).put_object(
        Key=key, Body=file_bytes, **extra_args
    )


def upload_file(file_bytes: bytes, filename: str, content_type: str | None) -> str:
    key = make_key(filename)
    put_bytes(key, file_bytes, content_type)
    return key


def download_file(key: str) -> bytes:
    return get_s3_resource().Bucket(settings.s3_bucket).Object(key).get()["Body"].read()


def get_file_url(key: str) -> str:
    client = get_s3_resource().meta.client
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=3600,
    )
