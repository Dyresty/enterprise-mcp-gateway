import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

from mcp.server.fastmcp import FastMCP

from app.gateway.tool_registry import ToolRegistry
from app.tools.calculator import add, multiply

from app.tools.github import (
    get_repository,
    get_issue,
    search_issues,
    list_repositories,
    create_issue,
    update_issue,
    add_issue_comment,
    delete_issue_comment,
)

from app.auth.rbac import authorize_tool, AuthorizationError
from app.auth.authentication import (
    AuthenticationContext,
    create_authentication_context,
)

from app.config import settings

from app.cache.redis_cache import RedisCache

from app.rate_limit.limiter import RateLimiter, RateLimitExceeded



mcp = FastMCP("Enterprise MCP Gateway")

registry = ToolRegistry()
cache = RedisCache()
rate_limiter = RateLimiter()

def build_cache_key(tool_name: str, arguments: dict) -> str:
    payload = json.dumps(
        arguments,
        sort_keys=True,
        separators=(",", ":"),
    )

    argument_hash = hashlib.sha256(
        payload.encode("utf-8")
    ).hexdigest()

    return f"mcp:tool:{tool_name}:{argument_hash}"

AUTH_CONTEXT: AuthenticationContext = create_authentication_context(
    settings.AUTH_USERNAME
)

def get_authorized_tool(tool_name: str) -> dict:
    """
    Retrieve a registered tool, authorize the current user,
    and enforce its rate limit.
    """

    tool = registry.get_tool(tool_name)

    if tool is None:
        raise ValueError(
            f"Tool '{tool_name}' is not registered or is disabled."
        )

    try:
        authorize_tool(
            user_role=AUTH_CONTEXT.user.role,
            tool=tool,
        )
    except AuthorizationError as exc:
        raise ValueError(str(exc)) from exc

    try:
        rate_limiter.check(
            user=AUTH_CONTEXT.user.username,
            tool_name=tool["name"],
            limit=tool.get("rate_limit_per_minute", 30),
        )
    except RateLimitExceeded as exc:
        raise ValueError(str(exc)) from exc

    return tool

def execute_with_timeout(
    tool: dict,
    execute_function,
):
    timeout_seconds = tool["timeout_seconds"]

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(execute_function)

        try:
            return future.result(timeout=timeout_seconds)

        except FutureTimeoutError as exc:
            future.cancel()

            raise TimeoutError(
                f"Tool '{tool['name']}' timed out after "
                f"{timeout_seconds} seconds."
            ) from exc

def execute_with_cache(
    tool_name: str,
    arguments: dict,
    execute_function,
):
    tool = get_authorized_tool(tool_name)

    if not tool["cache_enabled"]:
        return execute_function()

    cache_key = build_cache_key(
        tool_name,
        arguments,
    )

    cached_result = cache.get(cache_key)

    if cached_result is not None:
        return cached_result

    result = execute_function()

    cache.set(
        cache_key,
        result,
        tool["cache_ttl_seconds"],
    )

    return result

@mcp.tool(name="add")
def add_tool(a: int, b: int) -> int:
    """
    Add two integers and return the result.
    """
    get_authorized_tool("add")

    return add(a, b)

@mcp.tool(name="multiply")
def multiply_tool(a: int, b: int) -> int:
    """
    Multiply two integers and return the result.
    """
    get_authorized_tool("multiply")

    return multiply(a, b)



@mcp.tool(name="github.get_repository")
def github_get_repository(owner: str, repo: str) -> dict:
    """
    Retrieve metadata and information about a GitHub repository.
    """

    arguments = {
        "owner": owner,
        "repo": repo,
    }

    return execute_with_cache(
        tool_name="github.get_repository",
        arguments=arguments,
        execute_function=lambda: get_repository(
            owner=owner,
            repo=repo,
        ),
    )


@mcp.tool(name="github.get_issue")
def github_get_issue(
    owner: str,
    repo: str,
    issue_number: int,
) -> dict:
    """
    Retrieve a specific GitHub issue by issue number.
    """

    get_authorized_tool("github.get_issue")

    return get_issue(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
    )

@mcp.tool(name="github.search_issues")
def github_search_issues(
    owner: str,
    repo: str,
    query: str,
    state: str = "open",
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """
    Search GitHub issues in a repository.
    """

    get_authorized_tool("github.search_issues")

    return search_issues(
        owner=owner,
        repo=repo,
        query=query,
        state=state,
        page=page,
        per_page=per_page,
    )

@mcp.tool(name="github.list_repositories")
def github_list_repositories(
    page: int = 1,
    per_page: int = 30,
) -> dict:
    """
    List repositories accessible to the authenticated GitHub account.
    """

    get_authorized_tool("github.list_repositories")

    return list_repositories(
        page=page,
        per_page=per_page,
    )

@mcp.tool(name="github.create_issue")
def github_create_issue(
    owner: str,
    repo: str,
    title: str,
    body: str | None = None,
) -> dict:
    """
    Create a new GitHub issue.
    """

    get_authorized_tool("github.create_issue")

    return create_issue(
        owner=owner,
        repo=repo,
        title=title,
        body=body,
    )

@mcp.tool(name="github.update_issue")
def github_update_issue(
    owner: str,
    repo: str,
    issue_number: int,
    title: str | None = None,
    body: str | None = None,
    state: str | None = None,
) -> dict:
    """
    Update an existing GitHub issue.
    """

    get_authorized_tool("github.update_issue")

    return update_issue(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        title=title,
        body=body,
        state=state,
    )

@mcp.tool(name="github.add_issue_comment")
def github_add_issue_comment(
    owner: str,
    repo: str,
    issue_number: int,
    body: str,
) -> dict:
    """
    Add a comment to a GitHub issue.
    """

    get_authorized_tool("github.add_issue_comment")

    return add_issue_comment(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        body=body,
    )

@mcp.tool(name="github.delete_issue_comment")
def github_delete_issue_comment(
    owner: str,
    repo: str,
    issue_number: int,
    comment_id: int,
) -> dict:
    """
    Delete a comment from a GitHub issue.
    """

    get_authorized_tool("github.delete_issue_comment")

    return delete_issue_comment(
        owner=owner,
        repo=repo,
        issue_number=issue_number,
        comment_id=comment_id,
    )

if __name__ == "__main__":
    mcp.run()