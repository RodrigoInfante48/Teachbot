import os
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from app.models import AppendToNotionRequest, AppendToNotionResponse
from app.block_builder import build_notion_blocks
from app.notion_client import NotionClient

load_dotenv()

app = FastAPI(title="Teachbot Notion Middleware", version="1.0.0")


def _get_notion_client() -> NotionClient:
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="NOTION_TOKEN is not configured")
    return NotionClient(token)


@app.post("/append-to-notion", response_model=AppendToNotionResponse)
async def append_to_notion(payload: AppendToNotionRequest):
    client = _get_notion_client()
    notion_blocks = build_notion_blocks(payload.blocks)

    try:
        result = await client.append_blocks(payload.page_id, notion_blocks)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Notion API error: {exc}")

    results = result.get("results", [])
    return AppendToNotionResponse(
        success=True,
        appended_count=len(results),
        results=results,
    )
