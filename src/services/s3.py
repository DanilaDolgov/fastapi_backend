from src.config import settings
from aiobotocore.session import AioSession
from botocore.client import Config
from fastapi import UploadFile
import mimetypes


class S3Client:
    def __init__(self):
        self.bucket_name = settings.MINIO_BUCKET
        self.endpoint_internal = settings.MINIO_ENDPOINT_URL
        self.endpoint_public = settings.MINIO_PUBLIC_URL
        self.region = settings.MINIO_REGION
        self.aws_access_key = settings.MINIO_ACCESS_KEY
        self.aws_secret_key = settings.MINIO_SECRET_KEY
        self._session = AioSession()

    def _get_client(self, endpoint_url: str):
        """Создаём клиент для указанного endpoint"""
        return self._session.create_client(
            "s3",
            region_name=self.region,
            endpoint_url=endpoint_url,
            aws_secret_access_key=self.aws_secret_key,
            aws_access_key_id=self.aws_access_key,
            config=Config(signature_version="s3v4"),
        )

    async def upload_file(self, file: UploadFile, s3_key: str):
        """Загрузка файла на MinIO (internal endpoint)"""
        content_type, _ = mimetypes.guess_type(file.filename)
        if not content_type:
            content_type = "application/octet-stream"

        async with self._get_client(self.endpoint_internal) as client:
            data = await file.read()
            await client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=data,
                ContentType=content_type,
                ContentDisposition="inline"
            )
            print(f"Файл {file.filename} успешно загружен в {self.bucket_name}/{s3_key}")

    async def delete_files(self, prefix: str) -> dict:
        """Удаление всех файлов по префиксу (internal endpoint)"""
        async with self._get_client(self.endpoint_internal) as client:
            response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if "Contents" not in response:
                return {}

            keys = [{"Key": obj["Key"]} for obj in response["Contents"]]
            response = await client.delete_objects(
                Bucket=self.bucket_name,
                Delete={"Objects": keys, "Quiet": True}
            )
            return response

    async def list_keys(self, prefix: str) -> list[str]:
        """Получение списка ключей по префиксу (internal endpoint)"""
        async with self._get_client(self.endpoint_internal) as client:
            response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if "Contents" not in response:
                return []
            return [obj["Key"] for obj in response["Contents"]]

    async def generate_presigned_url(self, key: str, expires_in: int = 365 * 24 * 3600) -> str:
        """Генерация presigned URL для браузера"""
        async with self._get_client(self.endpoint_public) as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key, "ResponseContentDisposition": "inline"},
                ExpiresIn=expires_in
            )
            return url

    async def generate_presigned_urls_by_prefix(self, prefix: str, expires_in: int = 3600) -> list[str] | None:
        """Получаем presigned URL для всех объектов с заданным префиксом"""
        keys = await self.list_keys(prefix)
        if keys:
            urls = []
            for key in keys:
                url = await self.generate_presigned_url(key, expires_in)
                urls.append(url)
            return urls
        else:
            return None
