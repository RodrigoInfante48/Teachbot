# Teachbot Notion Middleware

A FastAPI service that receives a JSON payload from Make (automation platform), processes it through Gemini, and appends structured blocks to an existing Notion page via the Notion API v1.

## Local Setup

```bash
# 1. Clone the repo and enter the directory
git clone https://github.com/rodrigoinfante48/teachbot.git
cd teachbot

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and fill in NOTION_TOKEN and API_KEY (see below)

# 5. Start the development server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

## Environment Variables

| Variable | Description |
|---|---|
| `NOTION_TOKEN` | Notion integration secret. Create one at [notion.so/my-integrations](https://www.notion.so/my-integrations). The integration must have **Insert content** permission on the target page. |
| `API_KEY` | Arbitrary secret string used to authenticate requests via the `X-API-Key` header. Choose any strong random value (e.g. `openssl rand -hex 32`). |

Set these in your `.env` file locally, and as Railway environment variables in production (Railway dashboard → project → Variables).

## Railway Deployment

1. Push this repo to GitHub.
2. In Railway: **New Project → Deploy from GitHub repo** → select this repo.
3. Railway detects `railway.toml` / `Procfile` automatically — no extra build config needed.
4. Add the two environment variables (`NOTION_TOKEN`, `API_KEY`) in the Railway **Variables** tab.
5. Railway exposes a public URL (e.g. `https://teachbot-production.up.railway.app`). Use that as your Make endpoint.

## API Endpoint

### `POST /append-to-notion`

Appends structured blocks to an existing Notion page.

**Headers**

```
Content-Type: application/json
X-API-Key: <your API_KEY>
```

**Request body**

```json
{
  "page_id": "your-notion-page-id",
  "gemini_json": {
    "sections": [
      { "type": "heading_1", "content": "My Title" },
      { "type": "paragraph", "content": "Some body text." },
      { "type": "bulleted_list", "items": ["Point A", "Point B"] },
      { "type": "numbered_list", "items": ["Step 1", "Step 2"] },
      { "type": "callout", "content": "Important note" },
      { "type": "divider" }
    ]
  }
}
```

**Supported section types**

| `type` | Required fields |
|---|---|
| `heading_1` / `heading_2` / `heading_3` | `content` |
| `paragraph` | `content` |
| `bulleted_list` | `items` (array of strings) |
| `numbered_list` | `items` (array of strings) |
| `callout` | `content` |
| `divider` | _(none)_ |

**Response**

```json
{
  "success": true,
  "blocks_added": 6,
  "page_url": "https://www.notion.so/<page-id>"
}
```

### `GET /health`

Returns `{"status": "ok"}`. Used by Railway's health check.

## Make HTTP Module Configuration

In your Make scenario, add an **HTTP → Make a request** module with the following settings:

| Field | Value |
|---|---|
| **URL** | `https://<your-railway-url>/append-to-notion` |
| **Method** | `POST` |
| **Headers** | `Content-Type: application/json` and `X-API-Key: <your API_KEY>` |
| **Body type** | `Raw` |
| **Content type** | `JSON (application/json)` |

**Body mapping** — paste this template and replace the bracketed values with your Make variable references:

```json
{
  "page_id": "{{notion_page_id}}",
  "gemini_json": {{gemini_output}}
}
```

- `{{notion_page_id}}` → the Notion page ID variable from an earlier module (e.g. a Notion "Get a page" or a data store lookup).
- `{{gemini_output}}` → the raw JSON text returned by the Gemini module (must be the full `{"sections": [...]}` object, not wrapped in quotes).

Ensure the Gemini module before this one returns **only** the JSON object (no markdown fences). Set **Parse response** to `Yes` if you need to use individual fields downstream.

## Updating the Gemini Prompt

The prompt lives in `app/gemini_prompt.py` as the `TEACHBOT_PROMPT` constant. To change what Teachbot generates:

1. Open `app/gemini_prompt.py`.
2. Edit the natural-language instructions inside `TEACHBOT_PROMPT`.
   - The `OUTPUT SCHEMA` block defines the JSON structure the model must return — keep it in sync with `app/models.py` (`GeminiSection`) if you add new section types.
   - The `SECTION STRUCTURE` block controls the order and content of each section in the Teacher's Guide.
   - The `{student_data}` placeholder at the bottom is filled at runtime with the student's diagnostic information — do not remove it.
3. Save the file, commit, and push. Railway will redeploy automatically.

**In Make**, the Gemini module's system prompt or user message should call `TEACHBOT_PROMPT` (injected by the FastAPI app) — no changes are needed in Make itself when you edit the Python file.

## Running Tests

```bash
pytest tests/
```
