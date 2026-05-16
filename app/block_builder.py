from typing import Any
from app.models import (
    Block,
    HeadingBlock,
    ParagraphBlock,
    BulletedListBlock,
    NumberedListBlock,
    TodoBlock,
    CodeBlock,
    DividerBlock,
    CalloutBlock,
    GeminiSection,
)


def _rich_text(text: str, bold: bool = False, italic: bool = False, code: bool = False, color: str = "default") -> list[dict]:
    annotations: dict[str, Any] = {
        "bold": bold,
        "italic": italic,
        "strikethrough": False,
        "underline": False,
        "code": code,
        "color": color,
    }
    return [{"type": "text", "text": {"content": text}, "annotations": annotations}]


def build_notion_block(block: Block) -> dict[str, Any]:
    if isinstance(block, HeadingBlock):
        return {
            "object": "block",
            "type": block.type,
            block.type: {"rich_text": _rich_text(block.text)},
        }

    if isinstance(block, ParagraphBlock):
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": _rich_text(block.text, bold=block.bold, italic=block.italic)},
        }

    if isinstance(block, BulletedListBlock):
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {"rich_text": _rich_text(block.text)},
        }

    if isinstance(block, NumberedListBlock):
        return {
            "object": "block",
            "type": "numbered_list_item",
            "numbered_list_item": {"rich_text": _rich_text(block.text)},
        }

    if isinstance(block, TodoBlock):
        return {
            "object": "block",
            "type": "to_do",
            "to_do": {"rich_text": _rich_text(block.text), "checked": block.checked},
        }

    if isinstance(block, CodeBlock):
        return {
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": _rich_text(block.text),
                "language": block.language,
            },
        }

    if isinstance(block, DividerBlock):
        return {"object": "block", "type": "divider", "divider": {}}

    if isinstance(block, CalloutBlock):
        return {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": _rich_text(block.text),
                "icon": {"type": "emoji", "emoji": block.icon},
            },
        }

    raise ValueError(f"Unknown block type: {type(block)}")


def build_notion_blocks(blocks: list[Block]) -> list[dict[str, Any]]:
    return [build_notion_block(b) for b in blocks]


def _parse_bold_rich_text(text: str) -> list[dict]:
    """Split on **...** markers and return rich_text segments with bold annotations."""
    parts = text.split("**")
    result = []
    for i, part in enumerate(parts):
        if not part:
            continue
        result.extend(_rich_text(part, bold=(i % 2 == 1)))
    return result or _rich_text("")


def convert_to_notion_blocks(sections: list[GeminiSection]) -> list[dict[str, Any]]:
    blocks: list[dict[str, Any]] = []
    for section in sections:
        t = section.type

        if t in ("heading_1", "heading_2", "heading_3"):
            blocks.append({
                "object": "block",
                "type": t,
                t: {"rich_text": _parse_bold_rich_text(section.content or "")},
            })

        elif t == "paragraph":
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": _parse_bold_rich_text(section.content or "")},
            })

        elif t == "bulleted_list":
            for item in (section.items or []):
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"rich_text": _parse_bold_rich_text(item)},
                })

        elif t == "numbered_list":
            for item in (section.items or []):
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {"rich_text": _parse_bold_rich_text(item)},
                })

        elif t == "divider":
            blocks.append({"object": "block", "type": "divider", "divider": {}})

        elif t == "callout":
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": _parse_bold_rich_text(section.content or ""),
                    "icon": {"type": "emoji", "emoji": "💡"},
                },
            })

    return blocks
