import httpx
from typing import Any

NOTION_API_VERSION = "2022-06-28"
NOTION_BASE_URL = "https://api.notion.com/v1"


class NotionClient:
    def __init__(self, token: str):
        self._headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_API_VERSION,
            "Content-Type": "application/json",
        }

    async def append_blocks(self, page_id: str, children: list[dict[str, Any]]) -> dict[str, Any]:
        url = f"{NOTION_BASE_URL}/blocks/{page_id}/children"
        # Notion caps appends at 100 blocks per request
        results: list[dict] = []
        for i in range(0, len(children), 100):
            chunk = children[i : i + 100]
            async with httpx.AsyncClient() as client:
                response = await client.patch(url, headers=self._headers, json={"children": chunk})
                response.raise_for_status()
                results.extend(response.json().get("results", []))
        return {"results": results}
