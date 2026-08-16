from app.integrations.github.client import GitHubClient


github_client = GitHubClient()


def get_repository(owner: str, repo: str) -> dict:
    return github_client.get_repository(owner, repo)