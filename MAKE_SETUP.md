# Make Scenario Setup Guide

Step-by-step instructions for configuring the Teachbot Make scenario to route
through the Railway middleware instead of calling the Notion API directly.

---

## Module order after changes

```
[Trigger] → [Notion: Get page (5)] → [Gemini] → [JSON Parse] → [HTTP: POST /append-to-notion]
```

Module 7 (Notion Append) is removed.

---

## 1. Gemini module — expect JSON output

Open the Gemini module and make the following change so that downstream modules
can parse its output without stripping markdown fences.

| Setting | Value |
|---|---|
| **Parse response** | `Yes` |
| **Response format** (system prompt instruction) | Instruct the model to return **only** a raw JSON object — no markdown code fences, no explanation. Example addition to the system prompt: `"Return only valid JSON. Do not wrap the response in markdown fences."` |

The model's output must be exactly:

```json
{
  "sections": [
    { "type": "heading_1", "content": "..." },
    ...
  ]
}
```

---

## 2. JSON Parse module — parse Gemini output

Add a **Tools → JSON → Parse JSON** module immediately after the Gemini module.

| Setting | Value |
|---|---|
| **JSON string** | Map the Gemini module's text/content output field (the raw JSON string) |

After this module runs, individual fields such as `sections` are available as
structured data for mapping in later modules.

---

## 3. HTTP module — replace the Notion Append module

Add an **HTTP → Make a request** module after the JSON Parse module.
Delete (or disable) the old Notion Append module (module 7) **after** wiring
this one up.

### URL

```
https://<your-railway-url>/append-to-notion
```

Replace `<your-railway-url>` with the public domain shown in the Railway
dashboard (e.g. `teachbot-production.up.railway.app`).

### Method

`POST`

### Headers

Add two headers:

| Header name | Header value |
|---|---|
| `X-API-Key` | Your `API_KEY` environment variable value |
| `Content-Type` | `application/json` |

### Body

| Setting | Value |
|---|---|
| **Body type** | `Raw` |
| **Content type** | `JSON (application/json)` |

Paste the following JSON body template and replace the bracketed references
with Make variable mappings:

```json
{
  "page_id": "{{5.id}}",
  "gemini_json": {{geminiOutput}}
}
```

**Mapping guide:**

| Placeholder | Source | Notes |
|---|---|---|
| `{{5.id}}` | Notion module 5 → `id` field | The Notion page ID retrieved earlier in the scenario |
| `{{geminiOutput}}` | JSON Parse module → root object | Map the entire parsed object, not a stringified version — Make will serialise it correctly when Body type is Raw/JSON |

> **Tip:** In the Make body editor, click the mapped variable for
> `gemini_json` and select the JSON Parse module's output bundle root
> (not a nested key). This ensures the full `{"sections": [...]}` object is
> sent, not just a string.

### Expected response

The Railway service returns:

```json
{
  "success": true,
  "blocks_added": 6,
  "page_url": "https://www.notion.so/<page-id>"
}
```

Set **Parse response** to `Yes` if you need `blocks_added` or `page_url` in a
later module.

---

## 4. Remove old Notion Append module (module 7)

1. Right-click module 7 in the scenario canvas.
2. Select **Delete module**.
3. Confirm deletion.

The HTTP module added in step 3 fully replaces its function.

---

## Verification checklist

- [ ] Gemini module returns plain JSON (no fences) when run manually.
- [ ] JSON Parse module shows structured `sections` array in the output panel.
- [ ] HTTP module shows `"success": true` in the response after a test run.
- [ ] No errors appear for module 7 (it no longer exists).
- [ ] The target Notion page contains the new blocks after a full scenario run.
