from src.config import settings

from fastapi import UploadFile
import mimetypes

class S3Client:
    def __init__(self):
        self.bucket_name = settings.MINIO_BUCKET

    async def upload_file(self, client, file: UploadFile, s3_key: str):
        """Загрузка файла на S3 через переданный клиент"""
        content_type, _ = mimetypes.guess_type(file.filename)
        if not content_type:
            content_type = "application/octet-stream"

        data = await file.read()
        await client.put_object(
            Bucket=self.bucket_name,
            Key=s3_key,
            Body=data,
            ContentType=content_type,
            ContentDisposition="inline",
        )
        print(f"Файл {file.filename} успешно загружен в {self.bucket_name}/{s3_key}")

    async def delete_files(self, client, prefix: str) -> dict:
        """Удаление всех файлов по префиксу"""
        response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        if "Contents" not in response:
            return {}

        keys = [{"Key": obj["Key"]} for obj in response["Contents"]]
        response = await client.delete_objects(
            Bucket=self.bucket_name, Delete={"Objects": keys, "Quiet": True}
        )
        return response

    async def list_keys(self, client, prefix: str) -> list[str]:
        response = await client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        if "Contents" not in response:
            return []
        return [obj["Key"] for obj in response["Contents"]]

    async def generate_presigned_url(self, client, key: str, expires_in: int = 365 * 24 * 3600) -> str:
        url = await client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
                "ResponseContentDisposition": "inline",
            },
            ExpiresIn=expires_in,
        )
        return url

    async def generate_presigned_urls_by_prefix(
        self, client, prefix: str, expires_in: int = 3600
    ) -> list[str] | None:
        keys = await self.list_keys(client, prefix)
        if keys:
            urls = [await self.generate_presigned_url(client, key, expires_in) for key in keys]
            return urls
        return None
