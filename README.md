# Teachbot Notion Middleware

A FastAPI service that receives a JSON payload from Make (automation platform) and appends structured blocks to an existing Notion page via the Notion API v1.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set your NOTION_TOKEN
```

Your Notion integration must have **Insert content** permission on the target page.

## Running

```bash
uvicorn app.main:app --reload
```

## Endpoint

### `POST /append-to-notion`

Appends one or more blocks to an existing Notion page.

**Request body**

```json
{
  "page_id": "your-notion-page-id",
  "blocks": [
    { "type": "heading_1", "text": "My Title" },
    { "type": "paragraph", "text": "Some body text.", "bold": false, "italic": false },
    { "type": "bulleted_list_item", "text": "Bullet point" },
    { "type": "numbered_list_item", "text": "Step one" },
    { "type": "to_do", "text": "A task", "checked": false },
    { "type": "code", "text": "print('hello')", "language": "python" },
    { "type": "divider" },
    { "type": "callout", "text": "Important note", "icon": "💡" }
  ]
}
```

**Supported block types**

| `type`               | Extra fields                              |
|----------------------|-------------------------------------------|
| `heading_1`          | `text`                                    |
| `heading_2`          | `text`                                    |
| `heading_3`          | `text`                                    |
| `paragraph`          | `text`, `bold`, `italic`                  |
| `bulleted_list_item` | `text`                                    |
| `numbered_list_item` | `text`                                    |
| `to_do`              | `text`, `checked`                         |
| `code`               | `text`, `language` (default: plain text)  |
| `divider`            | _(none)_                                  |
| `callout`            | `text`, `icon` (emoji, default: 💡)       |

**Response**

```json
{
  "success": true,
  "appended_count": 3,
  "results": [ ... ]
}
```

## Running tests

```bash
pytest tests/
```

## Make integration

In your Make scenario, add an **HTTP > Make a request** module pointed at:

```
POST http://<your-host>/append-to-notion
Content-Type: application/json
```

Map your scenario data to the JSON schema above.
