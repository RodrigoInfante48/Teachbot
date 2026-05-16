from pydantic import BaseModel, Field
from typing import Any, Literal, Optional


class TextContent(BaseModel):
    text: str
    bold: bool = False
    italic: bool = False
    code: bool = False
    color: str = "default"


class HeadingBlock(BaseModel):
    type: Literal["heading_1", "heading_2", "heading_3"]
    text: str


class ParagraphBlock(BaseModel):
    type: Literal["paragraph"]
    text: str
    bold: bool = False
    italic: bool = False


class BulletedListBlock(BaseModel):
    type: Literal["bulleted_list_item"]
    text: str


class NumberedListBlock(BaseModel):
    type: Literal["numbered_list_item"]
    text: str


class TodoBlock(BaseModel):
    type: Literal["to_do"]
    text: str
    checked: bool = False


class CodeBlock(BaseModel):
    type: Literal["code"]
    text: str
    language: str = "plain text"


class DividerBlock(BaseModel):
    type: Literal["divider"]


class CalloutBlock(BaseModel):
    type: Literal["callout"]
    text: str
    icon: str = "💡"


Block = (
    HeadingBlock
    | ParagraphBlock
    | BulletedListBlock
    | NumberedListBlock
    | TodoBlock
    | CodeBlock
    | DividerBlock
    | CalloutBlock
)


class GeminiSection(BaseModel):
    type: Literal[
        "heading_1", "heading_2", "heading_3",
        "paragraph", "bulleted_list", "numbered_list",
        "divider", "callout",
    ]
    content: Optional[str] = None
    items: Optional[list[str]] = None


class GeminiInput(BaseModel):
    sections: list[GeminiSection]


class AppendToNotionRequest(BaseModel):
    page_id: str = Field(..., description="Notion page ID to append blocks to")
    blocks: list[Block] = Field(..., description="List of blocks to append")


class AppendToNotionResponse(BaseModel):
    success: bool
    appended_count: int
    results: list[dict[str, Any]]
