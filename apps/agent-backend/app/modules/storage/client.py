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


def upload_file(file_bytes: bytes, filename: str, content_type: str | None) -> str:
    key = f"{uuid.uuid4()}-{filename}"
    extra_args = {"ContentType": content_type} if content_type else {}
    get_s3_resource().Bucket(settings.s3_bucket).put_object(
        Key=key, Body=file_bytes, **extra_args
    )
    return key


def get_file_url(key: str) -> str:
    client = get_s3_resource().meta.client
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=3600,
    )
