from aiobotocore.session import AioSession
from botocore.client import Config
from src.config import settings


class S3Client:
    """Асинхронный клиент для MinIO/S3 с переиспользуемой aio-сессией."""

    def __init__(self, public: bool = False):
        self._session: AioSession | None = None
        self._initialized = False
        self._public = public
        self._client_ctx = None
        self._client = None

    async def init(self):
        """Создаёт aio-сессию (один раз за приложение)."""
        if not self._initialized:
            self._session = AioSession()
            self._initialized = True

    def use_public(self, value: bool = True):
        """Переключает endpoint (внутренний/публичный)."""
        self._public = value

    async def get_client(self, public: bool | None = None):
        """Возвращает асинхронный контекстный менеджер клиента."""
        if not self._initialized or not self._session:
            raise RuntimeError("S3Client не инициализирован. Вызови init() перед использованием.")

        public = self._public if public is None else public
        endpoint = settings.MINIO_PUBLIC_URL if public else settings.MINIO_ENDPOINT_URL

        return self._session.create_client(
            "s3",
            region_name=settings.MINIO_REGION,
            endpoint_url=endpoint,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version="s3v4"),
        )

    async def __aenter__(self):
        """Открывает контекст клиента автоматически."""
        if not self._initialized:
            await self.init()

        self._client_ctx = await self.get_client(self._public)
        self._client = await self._client_ctx.__aenter__()
        return self._client

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрывает клиента."""
        if self._client_ctx:
            await self._client_ctx.__aexit__(exc_type, exc_val, exc_tb)
        self._client_ctx = None
        self._client = None

    async def shutdown(self):
        """Закрывает сессию."""
        self._session = None
        self._initialized = False
