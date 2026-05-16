import os
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv

from app.models import AppendToNotionRequest, AppendToNotionResponse
from app.block_builder import convert_to_notion_blocks
from app.notion_client import NotionClient

load_dotenv()

app = FastAPI(title="Teachbot Notion Middleware", version="1.0.0")

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def _verify_api_key(api_key: str = Security(_api_key_header)) -> str:
    expected = os.getenv("API_KEY")
    if not expected or api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return api_key


def _get_notion_client() -> NotionClient:
    token = os.getenv("NOTION_TOKEN")
    if not token:
        raise HTTPException(status_code=500, detail="NOTION_TOKEN is not configured")
    return NotionClient(token)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/append-to-notion", response_model=AppendToNotionResponse)
async def append_to_notion(
    payload: AppendToNotionRequest,
    _: str = Security(_verify_api_key),
):
    client = _get_notion_client()
    notion_blocks = convert_to_notion_blocks(payload.gemini_json.sections)

    result = await client.append_blocks(payload.page_id, notion_blocks)

    if not result["success"]:
        raise HTTPException(status_code=502, detail=f"Notion API error: {result['error']}")

    page_id_clean = payload.page_id.replace("-", "")
    return AppendToNotionResponse(
        success=True,
        blocks_added=result["blocks_added"],
        page_url=f"https://www.notion.so/{page_id_clean}",
    )
