import mimetypes
import asyncio
from typing import List
from src.config import settings
from src.schemas.files_dto import FileDTO
from src.utils.s3_client import S3Client


class S3Manager:
    """Управление файлами в S3 (загрузка, удаление, генерация ссылок)."""

    def __init__(self, client: S3Client):
        self.bucket_name = settings.MINIO_BUCKET
        self._client = client

    async def upload_file(self, file: FileDTO, s3_key: str):
        """Загрузка одного файла."""
        content_type, _ = mimetypes.guess_type(file.filename)
        if not content_type:
            content_type = "application/octet-stream"

        async with self._client as client:
            await client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file.file,
                ContentType=content_type,
                ContentDisposition="inline",
                ACL="private",
            )

    async def upload_files(self, files: List[FileDTO], prefix: str = ""):
        """Пакетная загрузка."""
        tasks = []
        for f in files:
            key = f"{prefix}/{f.filename}" if prefix else f.filename
            tasks.append(self.upload_file(f, key))
        await asyncio.gather(*tasks)

    async def delete_files(self, prefix: str):
        """Удаление по префиксу."""
        async with self._client as client:
            response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if "Contents" not in response:
                return {}

            keys = [{"Key": obj["Key"]} for obj in response["Contents"]]
            return await client.delete_objects(
                Bucket=self.bucket_name,
                Delete={"Objects": keys, "Quiet": True}
            )

    async def list_keys(self, prefix: str):
        """Получить список ключей по префиксу."""
        async with self._client as client:
            response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if "Contents" not in response:
                return []
            return [obj["Key"] for obj in response["Contents"]]

    async def generate_presigned_url(self, key: str, expires_in: int = 3600):
        """Генерация публичной presigned URL."""
        self._client.use_public(True)
        async with self._client as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "ResponseContentDisposition": "inline",
                },
                ExpiresIn=expires_in,
            )
        self._client.use_public(False)
        return url

    async def generate_presigned_urls_by_prefix(self, prefix: str, expires_in: int = 3600):
        """Генерация presigned URL для всех файлов с префиксом."""
        keys = await self.list_keys(prefix)
        if not keys:
            return []
        urls = []
        for key in keys:
            url = await self.generate_presigned_url(key, expires_in)
            urls.append({key: url})
        return urls

    async def shutdown(self):
        await self._client.shutdown()
