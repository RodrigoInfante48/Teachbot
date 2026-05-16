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
