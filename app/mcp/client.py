import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="python",
    args=["-m", "app.mcp.server"],
    env=os.environ.copy(),
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            tools = await session.list_tools()

            print("Available tools:")

            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            result = await session.call_tool(
                "add",
                arguments={
                    "a": 10,
                    "b": 20,
                },
            )

            print("\nAdd result:")
            print(result)

            result = await session.call_tool(
                "multiply",
                arguments={
                    "a": 10,
                    "b": 20,
                },
            )

            print("\nMultiply result:")
            print(result)



            github_result = await session.call_tool(
                "github.get_repository",
                arguments={
                    "owner": "Dyresty",
                    "repo": "enterprise-hybrid-rag",
                },
            )

            print("\nGitHub repository:")
            print(github_result)

            search_result = await session.call_tool(
                "github.search_issues",
                arguments={
                    "owner": "Dyresty",
                    "repo": "enterprise-mcp-gateway",
                    "query": "authentication",
                    "state": "open",
                },
            )

            print("\nGitHub issue search:")
            print(search_result)


            get_issue_result = await session.call_tool(
                "github.get_issue",
                arguments={
                    "owner": "Dyresty",
                    "repo": "enterprise-mcp-gateway",
                    "issue_number": 1,
                },
            )

            print("\nGitHub issue:")
            print(get_issue_result)

            list_result = await session.call_tool(
                "github.list_repositories",
                arguments={
                    "page": 1,
                    "per_page": 5,
                },
            )

            print("\nGitHub repositories:")
            print(list_result)

            create_issue_result = await session.call_tool(
                "github.create_issue",
                arguments={
                    "owner": "Dyresty",
                    "repo": "enterprise-mcp-gateway",
                    "title": "MCP client create issue test",
                    "body": "Testing github.create_issue through the MCP client.",
                },
            )

            print("\nGitHub created issue:")
            print(create_issue_result)

            issue_data = json.loads(
                create_issue_result.content[0].text
            )

            issue_number = issue_data["number"]

            update_issue_result = await session.call_tool(
                "github.update_issue",
                arguments={
                    "owner": "Dyresty",
                    "repo": "enterprise-mcp-gateway",
                    "issue_number": issue_number,
                    "title": "MCP client updated issue test",
                },
            )

            print("\nGitHub updated issue:")
            print(update_issue_result)

            add_comment_result = await session.call_tool(
                "github.add_issue_comment",
                arguments={
                    "owner": "Dyresty",
                    "repo": "enterprise-mcp-gateway",
                    "issue_number": issue_number,
                    "body": "Testing github.add_issue_comment through the MCP client.",
                },
            )

            print("\nGitHub added issue comment:")
            print(add_comment_result)

            comment_data = json.loads(
                add_comment_result.content[0].text
            )

            comment_id = comment_data["id"]

            delete_comment_result = await session.call_tool(
                "github.delete_issue_comment",
                arguments={
                    "owner": "Dyresty",
                    "repo": "enterprise-mcp-gateway",
                    "issue_number": issue_number,
                    "comment_id": comment_id,
                },
            )

            print("\nGitHub deleted issue comment:")
            print(delete_comment_result)

            close_issue_result = await session.call_tool(
                "github.update_issue",
                arguments={
                    "owner": "Dyresty",
                    "repo": "enterprise-mcp-gateway",
                    "issue_number": issue_number,
                    "state": "closed",
                },
            )

            print("\nGitHub closed test issue:")
            print(close_issue_result)

if __name__ == "__main__":
    asyncio.run(main())