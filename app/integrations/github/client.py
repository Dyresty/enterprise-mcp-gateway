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

    def search_issues(
        self,
        owner: str,
        repo: str,
        query: str,
        state: str = "open",
        page: int = 1,
        per_page: int = 20,
    ) -> dict:

        url = f"{self.BASE_URL}/search/issues"

        params = {
            "q": f"{query} repo:{owner}/{repo} is:issue",
            "page": page,
            "per_page": per_page,
        }

        response = httpx.get(
            url,
            headers=self.headers,
            params=params,
            timeout=10.0,
        )

        if response.status_code != 200:
            print("GitHub response:")
            print(response.text)

        response.raise_for_status()

        data = response.json()

        issues = []

        for item in data.get("items", []):
            # GitHub search can return pull requests as well.
            if "pull_request" in item:
                continue

            if state != "all" and item.get("state") != state:
                continue

            issues.append(
                {
                    "number": item["number"],
                    "title": item["title"],
                    "state": item["state"],
                    "url": item["html_url"],
                    "created_at": item["created_at"],
                    "updated_at": item["updated_at"],
                }
            )

        return {
            "total_count": len(issues),
            "issues": issues,
        }