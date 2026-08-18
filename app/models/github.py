from typing import Literal

from pydantic import BaseModel, Field


class GitHubIssueSearchRequest(BaseModel):
    owner: str = Field(min_length=1)
    repo: str = Field(min_length=1)
    query: str = Field(min_length=1)
    state: Literal["open", "closed", "all"] = "open"

    page: int = Field(default=1, ge=1, le=10)
    per_page: int = Field(default=20, ge=1, le=100)


class GitHubIssueRequest(BaseModel):
    owner: str = Field(min_length=1)
    repo: str = Field(min_length=1)
    issue_number: int = Field(ge=1)

class GitHubCreateIssueRequest(BaseModel):
    owner: str = Field(min_length=1)
    repo: str = Field(min_length=1)
    title: str = Field(min_length=1, max_length=256)
    body: str | None = Field(default=None, max_length=10000)

class GitHubIssue(BaseModel):
    number: int
    title: str
    state: Literal["open", "closed"]
    url: str
    created_at: str
    updated_at: str


class GitHubIssueSearchResponse(BaseModel):
    total_count: int
    issues: list[GitHubIssue]

class GitHubRepositoryRequest(BaseModel):
    owner: str = Field(min_length=1)
    repo: str = Field(min_length=1)

class GitHubRepository(BaseModel):
    name: str
    full_name: str
    description: str | None
    language: str | None
    default_branch: str
    visibility: str
    open_issues: int
    stars: int
    forks: int
    created_at: str
    updated_at: str


class GitHubRepositoryListRequest(BaseModel):
    page: int = Field(default=1, ge=1, le=10)
    per_page: int = Field(default=30, ge=1, le=100)


class GitHubRepositoryListResponse(BaseModel):
    repositories: list[GitHubRepository]
    page: int
    per_page: int