import pytest
import asyncio
from io import BytesIO
from unittest.mock import AsyncMock

from src.utils.s3_client import S3Client
from src.utils.s3_manager import S3Manager
from src.schemas.files_dto import FileDTO


@pytest.mark.asyncio
async def test_s3_single_session_used_across_uploads(monkeypatch, capsys):
    """
    Проверяем, что при параллельных загрузках используется одна и та же AioSession,
    и выводим ID каждой клиентской сессии для наглядности.
    """

    s3_client = S3Client()
    await s3_client.init()
    s3_manager = S3Manager(s3_client=s3_client)

    # Мокаем S3 клиент
    mock_client = AsyncMock()
    mock_client.put_object.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

    created_clients = []

    def mock_create_client(*args, **kwargs):
        # Симулируем создание клиента и запоминаем его ID
        client_id = len(created_clients) + 1
        created_clients.append(client_id)

        class MockClientCtx:
            async def __aenter__(self_inner):
                print(f"[create_client] -> New mock client #{client_id} created, session_id={id(s3_client._session)}")
                return mock_client

            async def __aexit__(self_inner, exc_type, exc, tb):
                print(f"[close_client] -> Mock client #{client_id} closed")

        return MockClientCtx()

    monkeypatch.setattr(s3_client._session, "create_client", mock_create_client)

    async def upload_task(i):
        async with s3_client as client:
            print(f"[task-{i}] Using session id={id(s3_client._session)}")
            file_dto = FileDTO(
                filename=f"test_{i}.txt",
                content_type="text/plain",
                file=BytesIO(b"dummy content")
            )
            await s3_manager.upload_files(client, [file_dto], prefix=f"test/{i}")
            print(f"[task-{i}] Upload complete")

    # Запускаем 5 задач параллельно
    await asyncio.gather(*(upload_task(i) for i in range(5)))

    # Проверяем состояние
    assert s3_client._initialized is True
    assert s3_client._session is not None
    assert len(created_clients) == 5
    assert mock_client.put_object.call_count == 5

    # Выводим собранные данные
    print(f"\nSession id used for all tasks: {id(s3_client._session)}")
    print(f"Clients created: {created_clients}")

    await s3_client.shutdown()

    # Покажем вывод pytest при запуске
    captured = capsys.readouterr()
    print("\n=== TEST LOG OUTPUT ===")
    print(captured.out)
