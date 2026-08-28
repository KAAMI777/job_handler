from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.enums import ParserType


class CompanyBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    career_url: HttpUrl
    parser_type: ParserType
    active: bool = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    career_url: HttpUrl | None = None
    parser_type: ParserType | None = None
    active: bool | None = None


class CompanyRead(CompanyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    career_url: str
    last_scraped_at: datetime | None
    last_status: str | None
    consecutive_failures: int
    created_at: datetime
