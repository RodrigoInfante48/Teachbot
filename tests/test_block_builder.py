import pytest
from app.block_builder import build_notion_block, build_notion_blocks
from app.models import (
    HeadingBlock,
    ParagraphBlock,
    BulletedListBlock,
    NumberedListBlock,
    TodoBlock,
    CodeBlock,
    DividerBlock,
    CalloutBlock,
)


def test_heading_1():
    block = HeadingBlock(type="heading_1", text="Hello")
    result = build_notion_block(block)
    assert result["type"] == "heading_1"
    assert result["heading_1"]["rich_text"][0]["text"]["content"] == "Hello"


def test_heading_2():
    block = HeadingBlock(type="heading_2", text="Section")
    result = build_notion_block(block)
    assert result["type"] == "heading_2"


def test_heading_3():
    block = HeadingBlock(type="heading_3", text="Sub")
    result = build_notion_block(block)
    assert result["type"] == "heading_3"


def test_paragraph_plain():
    block = ParagraphBlock(type="paragraph", text="Hello world")
    result = build_notion_block(block)
    assert result["type"] == "paragraph"
    rt = result["paragraph"]["rich_text"][0]
    assert rt["text"]["content"] == "Hello world"
    assert rt["annotations"]["bold"] is False
    assert rt["annotations"]["italic"] is False


def test_paragraph_bold_italic():
    block = ParagraphBlock(type="paragraph", text="Styled", bold=True, italic=True)
    result = build_notion_block(block)
    rt = result["paragraph"]["rich_text"][0]
    assert rt["annotations"]["bold"] is True
    assert rt["annotations"]["italic"] is True


def test_bulleted_list():
    block = BulletedListBlock(type="bulleted_list_item", text="Item")
    result = build_notion_block(block)
    assert result["type"] == "bulleted_list_item"
    assert result["bulleted_list_item"]["rich_text"][0]["text"]["content"] == "Item"


def test_numbered_list():
    block = NumberedListBlock(type="numbered_list_item", text="Step 1")
    result = build_notion_block(block)
    assert result["type"] == "numbered_list_item"


def test_todo_unchecked():
    block = TodoBlock(type="to_do", text="Do something")
    result = build_notion_block(block)
    assert result["type"] == "to_do"
    assert result["to_do"]["checked"] is False


def test_todo_checked():
    block = TodoBlock(type="to_do", text="Done", checked=True)
    result = build_notion_block(block)
    assert result["to_do"]["checked"] is True


def test_code_block():
    block = CodeBlock(type="code", text="print('hi')", language="python")
    result = build_notion_block(block)
    assert result["type"] == "code"
    assert result["code"]["language"] == "python"
    assert result["code"]["rich_text"][0]["text"]["content"] == "print('hi')"


def test_code_block_default_language():
    block = CodeBlock(type="code", text="foo")
    result = build_notion_block(block)
    assert result["code"]["language"] == "plain text"


def test_divider():
    block = DividerBlock(type="divider")
    result = build_notion_block(block)
    assert result["type"] == "divider"
    assert result["divider"] == {}


def test_callout_default_icon():
    block = CalloutBlock(type="callout", text="Note this")
    result = build_notion_block(block)
    assert result["type"] == "callout"
    assert result["callout"]["icon"]["emoji"] == "💡"
    assert result["callout"]["rich_text"][0]["text"]["content"] == "Note this"


def test_callout_custom_icon():
    block = CalloutBlock(type="callout", text="Warning", icon="⚠️")
    result = build_notion_block(block)
    assert result["callout"]["icon"]["emoji"] == "⚠️"


def test_build_notion_blocks_multiple():
    blocks = [
        HeadingBlock(type="heading_1", text="Title"),
        ParagraphBlock(type="paragraph", text="Body"),
        DividerBlock(type="divider"),
    ]
    results = build_notion_blocks(blocks)
    assert len(results) == 3
    assert results[0]["type"] == "heading_1"
    assert results[1]["type"] == "paragraph"
    assert results[2]["type"] == "divider"


def test_build_notion_blocks_empty():
    assert build_notion_blocks([]) == []
