import os

import pytest
from pydantic import ValidationError

from app.integrations.filesystem.client import FileAccessError, FileSystemClient
from app.tools import filesystem


@pytest.fixture
def client(tmp_path):
    root = tmp_path / "workspace"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "guide.md").write_text("# Guide\nRetention is ten years.\n", encoding="utf-8")
    (root / "docs" / "data.csv").write_text("id,value\n1,ten\n", encoding="utf-8")
    (root / "image.png").write_bytes(b"\x89PNG")
    (tmp_path / "secret.txt").write_text("outside the sandbox", encoding="utf-8")
    return FileSystemClient(str(root))


def test_list_and_read_inside_sandbox(client):
    paths = [entry["path"] for entry in client.list_files("docs")]
    assert paths == ["docs/data.csv", "docs/guide.md"]
    assert client.read_file("docs/guide.md")["content"].startswith("# Guide")


@pytest.mark.parametrize("path", ["../secret.txt", "docs/../../secret.txt", "/etc/passwd", "C:/Windows/win.ini"])
def test_paths_outside_sandbox_are_rejected(client, path):
    with pytest.raises(FileAccessError):
        client.read_file(path)


def test_symlink_escaping_the_sandbox_is_rejected(client, tmp_path):
    link = client.root / "docs" / "link.txt"
    try:
        os.symlink(tmp_path / "secret.txt", link)
    except (OSError, NotImplementedError):
        pytest.skip("creating symlinks needs extra rights on this system")
    with pytest.raises(FileAccessError):
        client.read_file("docs/link.txt")
    assert "docs/link.txt" not in [e["path"] for e in client.list_files("docs")]


def test_binary_and_oversized_files_are_rejected(client, monkeypatch):
    with pytest.raises(FileAccessError, match="not allowed"):
        client.read_file("image.png")

    monkeypatch.setattr("app.integrations.filesystem.client.MAX_READ_BYTES", 5)
    with pytest.raises(FileAccessError, match="larger than"):
        client.read_file("docs/guide.md")


def test_search_returns_file_and_line(client):
    results = client.search_files("ten")
    assert {"path": "docs/data.csv", "line": 2, "text": "1,ten"} in results
    assert {"path": "docs/guide.md", "line": 2, "text": "Retention is ten years."} in results


def test_tool_layer_validates_input(client, monkeypatch):
    monkeypatch.setattr(filesystem, "filesystem_client", client)
    with pytest.raises(ValidationError):
        filesystem.search_files(query="a")
    with pytest.raises(ValidationError):
        filesystem.read_file(path="")
    assert filesystem.read_file("docs/guide.md")["path"] == "docs/guide.md"
