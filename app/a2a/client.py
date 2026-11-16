"""
Call the gateway agent as another agent would: resolve its agent card,
then send a message over A2A JSON-RPC.

    python -m app.a2a.client "Which projects work on quantum key distribution networks?"
"""

import argparse
import asyncio

from a2a.client import create_client
from a2a.helpers.proto_helpers import get_stream_response_text, new_text_message
from a2a.types import Role, SendMessageRequest

from app.config import settings


async def ask(question: str) -> str:
    client = await create_client(settings.A2A_URL)

    request = SendMessageRequest(
        message=new_text_message(question, role=Role.ROLE_USER),
    )

    parts = []
    async for response in client.send_message(request):
        text = get_stream_response_text(response)
        if text:
            parts.append(text)

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question")
    args = parser.parse_args()

    print(asyncio.run(ask(args.question)))


if __name__ == "__main__":
    main()
