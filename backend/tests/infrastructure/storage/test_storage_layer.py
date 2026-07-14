import os
import json
import pytest
import asyncio
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import UploadFile
from io import BytesIO

# Early mock to prevent database engine creation during import
with patch("sqlalchemy.ext.asyncio.create_async_engine"), \
     patch("sqlalchemy.ext.asyncio.async_sessionmaker"):
    from app.infrastructure.storage.filesystem_document_repository import FilesystemDocumentRepository
    from app.infrastructure.storage.local_storage_adapter import LocalStorageAdapter
    from app.infrastructure.storage.database_foundation import get_db_session, init_database

from app.domain.models import Document, Page

# --- FilesystemDocumentRepository Tests ---

class TestFilesystemDocumentRepository:
    @pytest.fixture
    def repo(self, tmp_path):
        return FilesystemDocumentRepository(tmp_path)

    @pytest.mark.asyncio
    async def test_save_and_get(self, repo):
        doc = Document(
            document_id="doc1",
            filename="test.pdf",
            pages=[Page(page_number=1, text="Hello world")],
            owner_id="user123"
        )
        await repo.save(doc)

        retrieved = await repo.get_by_id("doc1")
        assert retrieved is not None
        assert retrieved.document_id == "doc1"
        assert retrieved.filename == "test.pdf"
        assert len(retrieved.pages) == 1
        assert retrieved.pages[0].text == "Hello world"
        assert retrieved.owner_id == "user123"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, repo):
        retrieved = await repo.get_by_id("ghost")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_save_batch(self, repo):
        docs = [
            Document(document_id=f"d{i}", filename=f"f{i}", pages=[])
            for i in range(5)
        ]
        await repo.save_batch(docs)

        all_docs = await repo.list_all()
        assert len(all_docs) == 5
        ids = {d.document_id for d in all_docs}
        assert ids == {"d0", "d1", "d2", "d3", "d4"}

    @pytest.mark.asyncio
    async def test_list_all_pagination(self, repo):
        for i in range(10):
            doc = Document(document_id=f"doc{i:02d}", filename=f"f{i}", pages=[])
            await repo.save(doc)

        paged = await repo.list_all(limit=3, offset=2)
        assert len(paged) == 3
        # sorted by filename/path usually, doc02, doc03, doc04
        assert paged[0].document_id == "doc02"
        assert paged[1].document_id == "doc03"
        assert paged[2].document_id == "doc04"

    @pytest.mark.asyncio
    async def test_delete(self, repo):
        doc = Document(document_id="to_delete", filename="f", pages=[])
        await repo.save(doc)

        deleted = await repo.delete("to_delete")
        assert deleted is True
        assert await repo.get_by_id("to_delete") is None

        deleted_again = await repo.delete("to_delete")
        assert deleted_again is False

    @pytest.mark.asyncio
    async def test_corrupted_json(self, repo, tmp_path):
        # Create a corrupted file
        file_path = tmp_path / "corrupt.json"
        file_path.write_text("invalid json")

        with pytest.raises(json.JSONDecodeError):
            await repo.get_by_id("corrupt")

# --- LocalStorageAdapter Tests ---

class TestLocalStorageAdapter:
    @pytest.fixture
    def adapter(self, tmp_path):
        return LocalStorageAdapter(tmp_path)

    def test_save_success(self, adapter):
        content = b"test content"
        file_mock = MagicMock(spec=UploadFile)
        file_mock.filename = "test.pdf"
        file_mock.file = BytesIO(content)

        path = adapter.save(file_mock)
        assert path.exists()
        assert path.read_bytes() == content
        assert adapter.exists(path)

    def test_save_invalid_extension(self, adapter):
        file_mock = MagicMock(spec=UploadFile)
        file_mock.filename = "evil.exe"

        with pytest.raises(ValueError, match="not allowed"):
            adapter.save(file_mock)

    def test_delete(self, adapter, tmp_path):
        test_file = tmp_path / "delete_me.pdf"
        test_file.write_text("data")

        assert adapter.delete(test_file) is True
        assert not test_file.exists()
        assert adapter.delete(test_file) is False

    def test_save_exception_cleanup(self, adapter):
        file_mock = MagicMock(spec=UploadFile)
        file_mock.filename = "fail.pdf"
        # Mocking read to raise an error
        file_mock.file = MagicMock()
        file_mock.file.read.side_effect = Exception("Read error")

        with pytest.raises(OSError):
            adapter.save(file_mock)

        target_path = adapter.upload_dir / "fail.pdf"
        assert not target_path.exists()

    def test_path_traversal_protection(self, adapter, tmp_path):
        file_mock = MagicMock(spec=UploadFile)
        file_mock.filename = "../traversal.pdf"
        file_mock.file = BytesIO(b"traversal")

        path = adapter.save(file_mock)
        # Verify it's saved as 'traversal.pdf' inside upload_dir, not in parent
        assert path.name == "traversal.pdf"
        assert path.parent == adapter.upload_dir
        assert path.exists()

# --- DatabaseFoundation Tests ---

class TestDatabaseFoundation:
    @pytest.mark.asyncio
    async def test_get_db_session_success(self):
        with patch("app.infrastructure.storage.database_foundation.AsyncSessionLocal") as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value = mock_session
            mock_session.__aenter__.return_value = mock_session

            async for session in get_db_session():
                assert session == mock_session

            assert mock_session.close.called

    @pytest.mark.asyncio
    async def test_session_exception_handling(self):
        with patch("app.infrastructure.storage.database_foundation.AsyncSessionLocal") as mock_session_maker:
            mock_session = AsyncMock()
            mock_session_maker.return_value = mock_session
            mock_session.__aenter__.return_value = mock_session

            gen = get_db_session()
            try:
                await gen.__anext__()
                await gen.athrow(ValueError("Session error"))
            except (ValueError, StopAsyncIteration):
                pass

            assert mock_session.close.called

    @pytest.mark.asyncio
    async def test_init_database(self):
        with patch("app.infrastructure.storage.database_foundation.engine") as mock_engine:
            mock_conn = AsyncMock()
            mock_engine.begin.return_value.__aenter__.return_value = mock_conn

            await init_database()

            assert mock_conn.run_sync.called
