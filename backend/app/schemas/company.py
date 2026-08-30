from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.models.enums import ParserType


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    # The URL you have — a marketing careers page or the ATS board itself.
    career_url: HttpUrl
    # Omit to let the backend detect the ATS from career_url.
    parser_type: ParserType | None = None
    active: bool = True


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    career_url: HttpUrl | None = None
    parser_type: ParserType | None = None
    active: bool | None = None


class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    career_url: str
    source_url: str | None
    parser_type: ParserType
    active: bool
    last_scraped_at: datetime | None
    last_status: str | None
    consecutive_failures: int
    created_at: datetime


class AtsResolveRequest(BaseModel):
    url: HttpUrl


class AtsResolveResult(BaseModel):
    parser_type: ParserType
    career_url: str
