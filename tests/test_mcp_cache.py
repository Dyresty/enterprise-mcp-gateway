from app.mcp import server


def test_build_cache_key_is_deterministic():
    arguments = {
        "owner": "Dyresty",
        "repo": "enterprise-mcp-gateway",
        "issue_number": 1,
    }

    key1 = server.build_cache_key(
        "github.get_issue",
        arguments,
    )

    key2 = server.build_cache_key(
        "github.get_issue",
        arguments,
    )

    assert key1 == key2


def test_build_cache_key_changes_with_arguments():
    key1 = server.build_cache_key(
        "github.get_issue",
        {
            "owner": "Dyresty",
            "repo": "enterprise-mcp-gateway",
            "issue_number": 1,
        },
    )

    key2 = server.build_cache_key(
        "github.get_issue",
        {
            "owner": "Dyresty",
            "repo": "enterprise-mcp-gateway",
            "issue_number": 2,
        },
    )

    assert key1 != key2