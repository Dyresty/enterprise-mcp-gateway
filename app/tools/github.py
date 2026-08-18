from app.integrations.github.client import GitHubClient
from app.models.github import (
    GitHubIssueRequest,
    GitHubIssueSearchRequest,
    GitHubIssueSearchResponse,
    GitHubIssue,
    GitHubCreateIssueRequest,
    GitHubUpdateIssueRequest,
    GitHubRepositoryRequest,
    GitHubRepository,
    GitHubRepositoryListRequest,
    GitHubRepositoryListResponse,
)

github_client = GitHubClient()


def get_repository(
    owner: str,
    repo: str,
) -> GitHubRepository:

    request = GitHubRepositoryRequest(
        owner=owner,
        repo=repo,
    )

    result = github_client.get_repository(
        owner=request.owner,
        repo=request.repo,
    )

    return GitHubRepository(**result)

def get_issue(
    owner: str,
    repo: str,
    issue_number: int,
) -> GitHubIssue:
    request = GitHubIssueRequest(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
    )

    result = github_client.get_issue(
        owner=request.owner,
        repo=request.repo,
        issue_number=request.issue_number,
    )

    return GitHubIssue(**result)


def search_issues(
    owner: str,
    repo: str,
    query: str,
    state: str = "open",
    page: int = 1,
    per_page: int = 20,
) -> GitHubIssueSearchResponse:

    request = GitHubIssueSearchRequest(
        owner=owner,
        repo=repo,
        query=query,
        state=state,
        page=page,
        per_page=per_page,
    )

    result = github_client.search_issues(
        owner=request.owner,
        repo=request.repo,
        query=request.query,
        state=request.state,
        page=request.page,
        per_page=request.per_page,
    )

    return GitHubIssueSearchResponse(**result)

def list_repositories(
    page: int = 1,
    per_page: int = 30,
) -> GitHubRepositoryListResponse:

    request = GitHubRepositoryListRequest(
        page=page,
        per_page=per_page,
    )

    result = github_client.list_repositories(
        page=request.page,
        per_page=request.per_page,
    )

    return GitHubRepositoryListResponse(**result)

def create_issue(
    owner: str,
    repo: str,
    title: str,
    body: str | None = None,
) -> GitHubIssue:

    request = GitHubCreateIssueRequest(
        owner=owner,
        repo=repo,
        title=title,
        body=body,
    )

    result = github_client.create_issue(
        owner=request.owner,
        repo=request.repo,
        title=request.title,
        body=request.body,
    )

    return GitHubIssue(**result)

def update_issue(
    owner: str,
    repo: str,
    issue_number: int,
    title: str | None = None,
    body: str | None = None,
    state: str | None = None,
) -> GitHubIssue:

    request = GitHubUpdateIssueRequest(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        title=title,
        body=body,
        state=state,
    )

    result = github_client.update_issue(
        owner=request.owner,
        repo=request.repo,
        issue_number=request.issue_number,
        title=request.title,
        body=request.body,
        state=request.state,
    )

    return GitHubIssue(**result)