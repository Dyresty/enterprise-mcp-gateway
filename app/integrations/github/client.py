import httpx

from app.config import settings


class GitHubClient:

    BASE_URL = "https://api.github.com"

    def __init__(self):
        if not settings.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN is not configured.")

        self.headers = {
            "Authorization": f"Bearer {settings.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def get_repository(self, owner: str, repo: str) -> dict:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}"

        response = httpx.get(
            url,
            headers=self.headers,
            timeout=10.0,
        )

        response.raise_for_status()

        data = response.json()

        return {
            "name": data["name"],
            "full_name": data["full_name"],
            "description": data["description"],
            "language": data["language"],
            "default_branch": data["default_branch"],
            "visibility": data["visibility"],
            "open_issues": data["open_issues_count"],
            "stars": data["stargazers_count"],
            "forks": data["forks_count"],
            "created_at": data["created_at"],
            "updated_at": data["updated_at"],
        }