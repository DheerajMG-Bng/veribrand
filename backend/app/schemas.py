from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class Draft(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    channel: Literal['social', 'influencer', 'ad', 'email']
    text: str = Field(min_length=1, max_length=5000)
    @field_validator('title', 'text')
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError('Please enter text, not only whitespace.')
        return value

class VersionInput(BaseModel):
    text: str = Field(min_length=1, max_length=5000)
    @field_validator('text')
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError('Please enter draft text.')
        return value

class ReviewInput(BaseModel):
    use_ai: bool = True

class DecisionInput(BaseModel):
    decision: Literal['accepted', 'edited', 'rejected']
    edited_text: str | None = Field(default=None, max_length=5000)
    reason: str | None = Field(default=None, max_length=2000)

class ReasonInput(BaseModel):
    reason: str = Field(min_length=1, max_length=2000)

class ReturnInput(BaseModel):
    comment: str = Field(min_length=1, max_length=2000)

class CommentInput(BaseModel):
    text: str = Field(min_length=1, max_length=2000)

class KnowledgeInput(BaseModel):
    kind: Literal['guideline', 'fact', 'term', 'claim_rule']
    code: str = Field(pattern=r'^[A-Z]-\d{2,3}$')
    title: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=2000)
    meta: dict = Field(default_factory=dict)
    valid_until: date | None = None
