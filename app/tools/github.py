from app.integrations.github.client import GitHubClient
from app.models.github import (
    GitHubIssueRequest,
    GitHubIssueSearchRequest,
    GitHubIssueSearchResponse,
    GitHubIssue,
)

github_client = GitHubClient()


def get_repository(owner: str, repo: str) -> dict:
    return github_client.get_repository(owner, repo)


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