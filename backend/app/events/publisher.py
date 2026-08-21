import os

import httpx


N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")


def publish_event(payload: dict) -> None:
    if not N8N_WEBHOOK_URL:
        return

    try:
        httpx.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=5.0,
        )
    except httpx.HTTPError:
        # Event delivery must not break the engineering transaction.
        pass