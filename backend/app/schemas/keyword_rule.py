from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KeywordRuleBase(BaseModel):
    role: str = Field(min_length=1, max_length=50)
    keyword: str = Field(min_length=1, max_length=100)
    weight: int = Field(default=1, ge=1, le=100)
    is_active: bool = True


class KeywordRuleCreate(KeywordRuleBase):
    pass


class KeywordRuleUpdate(BaseModel):
    role: str | None = Field(default=None, min_length=1, max_length=50)
    keyword: str | None = Field(default=None, min_length=1, max_length=100)
    weight: int | None = Field(default=None, ge=1, le=100)
    is_active: bool | None = None


class KeywordRuleRead(KeywordRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
