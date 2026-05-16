import asyncio
import httpx
from typing import Any

NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"

_MAX_RETRIES = 5
_BLOCKS_PER_REQUEST = 100


class NotionClient:
    def __init__(self, token: str):
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }

    async def append_blocks(
        self, page_id: str, blocks: list[dict[str, Any]]
    ) -> dict[str, Any]:
        url = f"{NOTION_BASE_URL}/blocks/{page_id}/children"
        all_results: list[dict] = []

        for i in range(0, max(len(blocks), 1), _BLOCKS_PER_REQUEST):
            chunk = blocks[i : i + _BLOCKS_PER_REQUEST]
            result = await self._patch_with_retry(url, {"children": chunk})
            if not result["success"]:
                return {
                    "success": False,
                    "blocks_added": len(all_results),
                    "error": result["error"],
                }
            all_results.extend(result["results"])

        return {"success": True, "blocks_added": len(all_results), "error": None}

    async def _patch_with_retry(
        self, url: str, payload: dict[str, Any]
    ) -> dict[str, Any]:
        delay = 0.5
        async with httpx.AsyncClient() as client:
            for attempt in range(_MAX_RETRIES):
                try:
                    response = await client.patch(
                        url, headers=self._headers, json=payload
                    )

                    if response.status_code == 429:
                        retry_after = float(
                            response.headers.get("Retry-After", delay)
                        )
                        await asyncio.sleep(retry_after)
                        delay = min(delay * 2, 60)
                        continue

                    response.raise_for_status()
                    return {
                        "success": True,
                        "results": response.json().get("results", []),
                        "error": None,
                    }

                except httpx.HTTPStatusError as exc:
                    # Non-rate-limit HTTP errors are not retried
                    return {
                        "success": False,
                        "results": [],
                        "error": f"HTTP {exc.response.status_code}: {exc.response.text}",
                    }
                except httpx.RequestError as exc:
                    if attempt == _MAX_RETRIES - 1:
                        return {
                            "success": False,
                            "results": [],
                            "error": f"Request failed: {exc}",
                        }
                    await asyncio.sleep(delay)
                    delay = min(delay * 2, 60)

        return {
            "success": False,
            "results": [],
            "error": "Exceeded maximum retries due to rate limiting",
        }
