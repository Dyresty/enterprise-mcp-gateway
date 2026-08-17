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