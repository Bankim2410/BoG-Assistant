"""
s3_storage.py — AWS S3 helpers for document storage.

All PDFs are stored under the prefix  pdfs/<filename>
"""

import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

BUCKET = os.getenv("S3_BUCKET_NAME", "")
PREFIX = "pdfs/"

_s3 = None


def _client():
    global _s3
    if _s3 is None:
        _s3 = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION", "ap-south-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
    return _s3


def s3_key(filename: str) -> str:
    return f"{PREFIX}{filename}"


def upload_file(local_path: str, filename: str) -> str:
    """Upload a local file to S3. Returns the S3 key."""
    key = s3_key(filename)
    _client().upload_file(local_path, BUCKET, key)
    print(f"☁️  Uploaded {filename} → s3://{BUCKET}/{key}")
    return key


def upload_bytes(data: bytes, filename: str) -> str:
    """Upload raw bytes to S3. Returns the S3 key."""
    key = s3_key(filename)
    _client().put_object(Bucket=BUCKET, Key=key, Body=data)
    print(f"☁️  Uploaded {filename} → s3://{BUCKET}/{key}")
    return key


def download_to_path(filename: str, local_path: str):
    """Download a file from S3 to a local path."""
    key = s3_key(filename)
    _client().download_file(BUCKET, key, local_path)
    print(f"⬇️  Downloaded s3://{BUCKET}/{key} → {local_path}")


def download_bytes(filename: str) -> bytes:
    """Return file content as bytes without touching disk."""
    key = s3_key(filename)
    obj = _client().get_object(Bucket=BUCKET, Key=key)
    return obj["Body"].read()


def list_pdfs() -> list[str]:
    """Return a list of filenames stored under the pdfs/ prefix."""
    paginator = _client().get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=BUCKET, Prefix=PREFIX)
    names = []
    for page in pages:
        for obj in page.get("Contents", []):
            name = obj["Key"].removeprefix(PREFIX)
            if name.endswith(".pdf"):
                names.append(name)
    return names


def file_exists(filename: str) -> bool:
    try:
        _client().head_object(Bucket=BUCKET, Key=s3_key(filename))
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            return False
        raise


def delete_file(filename: str):
    key = s3_key(filename)
    _client().delete_object(Bucket=BUCKET, Key=key)
    print(f"🗑️  Deleted s3://{BUCKET}/{key}")


def presigned_url(filename: str, expiry: int = 3600) -> str:
    """Generate a temporary download URL."""
    key = s3_key(filename)
    return _client().generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=expiry,
    )
