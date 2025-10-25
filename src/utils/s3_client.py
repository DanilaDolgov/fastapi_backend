from aiobotocore.session import AioSession
from botocore.client import Config

from src.config import settings

class S3Client:
    """Менеджер S3 через aiobotocore с поддержкой async контекста."""

    def __init__(self, internal: bool = True):
        self._session: AioSession | None = None
        self._initialized = False
        self._internal = internal
        self._client_ctx = None
        self._client = None

    async def init(self):
        if not self._initialized:
            self._session = AioSession()
            self._initialized = True

    async def shutdown(self):
        self._session = None
        self._initialized = False

    async def __aenter__(self):
        if not self._initialized or not self._session:
            raise RuntimeError("S3Manager не инициализирован. Вызови init() перед использованием.")

        endpoint = settings.MINIO_ENDPOINT_URL if self._internal else settings.MINIO_PUBLIC_URL

        self._client_ctx = self._session.create_client(
            "s3",
            region_name=settings.MINIO_REGION,
            endpoint_url=endpoint,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4"),
        )

        self._client = await self._client_ctx.__aenter__()
        return self._client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client_ctx:
            await self._client_ctx.__aexit__(exc_type, exc_val, exc_tb)
        self._client_ctx = None
        self._client = None
