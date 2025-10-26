from contextlib import asynccontextmanager
from typing import List
import mimetypes
import asyncio
from urllib.parse import urlparse, urlunparse

from src.config import settings
from src.schemas.files_dto import FileDTO
from src.utils.s3_client import S3Client


class S3Manager:
    def __init__(self, s3_client: S3Client):
        self.bucket_name = settings.MINIO_BUCKET
        self._s3_client = s3_client
        self._client = None

    @asynccontextmanager
    async def client_context(self):
        """Контекст, который открывает клиента один раз."""
        if not self._s3_client._initialized:
            await self._s3_client.init()

        if self._client is None:
            self._client = await self._s3_client.__aenter__()
            print(f"[DEBUG S3] client id={id(self._client)}, session id={id(self._s3_client._session)}")

        try:
            yield self._client
            print(f"[DEBUG S3] client id={id(self._client)}, session id={id(self._s3_client._session)}")
        finally:
            pass

    async def _upload_file_with_client(self, client, file: FileDTO, s3_key: str):
        content_type, _ = mimetypes.guess_type(file.filename)
        if not content_type:
            content_type = "application/octet-stream"

        await client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=file.file,
            ContentType=content_type,
            ContentDisposition="inline",
        )
        print(f"Файл {file.filename} успешно загружен в {self.bucket_name}/{s3_key}")

    async def upload_file(self, file: FileDTO, s3_key: str):
        async with self.client_context() as client:
            await self._upload_file_with_client(client, file, s3_key)

    async def upload_files(self, files: List[FileDTO], prefix: str = ""):
        async with self.client_context() as client:
            tasks = []
            for f in files:
                s3_key = f"{prefix}/{f.filename}" if prefix else f.filename
                tasks.append(self._upload_file_with_client(client, f, s3_key))
            await asyncio.gather(*tasks)

    async def delete_files(self, prefix: str) -> dict:
        async with self.client_context() as client:
            response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if "Contents" not in response:
                return {}

            keys = [{"Key": obj["Key"]} for obj in response["Contents"]]
            response = await client.delete_objects(
                Bucket=self.bucket_name, Delete={"Objects": keys, "Quiet": True}
            )
            return response

    async def list_keys(self, prefix: str) -> List[str]:
        async with self.client_context() as client:
            response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
            if "Contents" not in response:
                return []
            return [obj["Key"] for obj in response["Contents"]]

    async def generate_presigned_url(self, key: str, expires_in: int = 365 * 24 * 3600) -> str:
        async with self.client_context() as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "ResponseContentDisposition": "inline",
                },
                ExpiresIn=expires_in,
            )
            parsed = urlparse(url)
            public_parsed = urlparse(settings.MINIO_PUBLIC_URL)

            new_url = urlunparse((
                public_parsed.scheme or parsed.scheme,
                public_parsed.netloc or parsed.netloc,
                parsed.path,
                parsed.params,
                parsed.query,
                parsed.fragment
            ))

            return new_url

    async def generate_presigned_urls_by_prefix(self, prefix: str, expires_in: int = 3600) -> List[dict] | None:
        keys = await self.list_keys(prefix)
        if keys:
            urls = [{f"{key}": await self.generate_presigned_url(key, expires_in)} for key in keys]
            return urls
        return None

    async def shutdown(self):
        """Закрываем клиент S3 и сессию при завершении приложения."""
        if self._client is not None:
            await self._s3_client.__aexit__(None, None, None)
            self._client = None
