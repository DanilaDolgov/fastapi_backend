from src.config import settings

from aiobotocore.session import AioSession
from botocore.client import Config
from fastapi import UploadFile
import mimetypes


class S3Client:
    def __init__(self):
        self.bucket_name = settings.MINIO_BUCKET
        self.endpoint_url = settings.MINIO_ENDPOINT_URL
        self.region = settings.MINIO_REGION
        self.aws_access_key = settings.MINIO_ACCESS_KEY
        self.aws_secret_key = settings.MINIO_SECRET_KEY
        self._session = AioSession()

    def get_client(self):
        return self._session.create_client(
            "s3",
            region_name=self.region,
            endpoint_url=self.endpoint_url,
            aws_secret_access_key=self.aws_secret_key,
            aws_access_key_id=self.aws_access_key,
            config=Config(signature_version="s3v4"),
        )

    async def generate_presigned_urls_by_prefix(
            self, prefix: str, expires_in: int = 3600
    ) -> list[dict]:
        async with self.get_client() as client:
            response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if "Contents" not in response:
                return []
            urls = []
            for obj in response["Contents"]:
                key = obj["Key"]
                url = await client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": self.bucket_name,
                        "Key": key,
                        "ResponseContentDisposition": "inline"
                    },
                    ExpiresIn=expires_in
                )
                urls.append({f'{key}': f'{url}'})
            return urls

    async def get_download_url(self, key: str, expires_in: int = 3600) -> str:
        async with self.get_client() as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in,
            )
            return url

    async def upload_file(self, file: UploadFile, s3_key: str):
        content_type, _ = mimetypes.guess_type(file.filename)
        if not content_type:
            content_type = "application/octet-stream"
        async with self.get_client() as client:
            data = await file.read()
            await client.put_object(Bucket=self.bucket_name, Key=s3_key, Body=data, ContentType=content_type, ContentDisposition="inline")
            print(f"Файл {file.filename} успешно загружен в {self.bucket_name}/{s3_key}")

    async def delete_files(self, prefix: str) -> dict:
        async with self.get_client() as client:
            response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if "Contents" not in response:
                return {}
            keys = []
            for obj in response["Contents"]:
                keys.append(obj["Key"])
            response = await client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    "Objects": [{"Key": key} for key in keys],
                    "Quiet": True
                },
            )
            return response