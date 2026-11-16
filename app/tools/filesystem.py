from pydantic import BaseModel, Field

from app.integrations.filesystem.client import FileSystemClient


class ListFilesRequest(BaseModel):
    path: str = Field(default=".", max_length=500)
    pattern: str = Field(default="*", max_length=100)


class ReadFileRequest(BaseModel):
    path: str = Field(min_length=1, max_length=500)


class SearchFilesRequest(BaseModel):
    query: str = Field(min_length=2, max_length=200)
    path: str = Field(default=".", max_length=500)


filesystem_client = FileSystemClient()


def list_files(path: str = ".", pattern: str = "*") -> list[dict]:
    request = ListFilesRequest(path=path, pattern=pattern)
    return filesystem_client.list_files(request.path, request.pattern)


def read_file(path: str) -> dict:
    request = ReadFileRequest(path=path)
    return filesystem_client.read_file(request.path)


def search_files(query: str, path: str = ".") -> list[dict]:
    request = SearchFilesRequest(query=query, path=path)
    return filesystem_client.search_files(request.query, request.path)
