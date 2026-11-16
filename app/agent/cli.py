"""
Ask the gateway agent a question from the command line.

    python -m app.agent.cli "Which EU projects work on explainable AI on knowledge graphs?"
    python -m app.agent.cli "Create an issue in Dyresty/enterprise-mcp-gateway" --user analyst
"""

import argparse
import asyncio

from app.agent.runner import run_agent
from app.agent.tracing import flush


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    parser.add_argument("--user", default="analyst", choices=["analyst", "developer", "admin"])
    args = parser.parse_args()

    result = asyncio.run(run_agent(args.question, args.user))

    for call in result["tool_calls"]:
        print(f"[tool] {call['tool']} {call['args']}")
    for error in result["tool_errors"]:
        print(f"[tool error] {error}")
    print()
    print(result["answer"])

    flush()


if __name__ == "__main__":
    main()
