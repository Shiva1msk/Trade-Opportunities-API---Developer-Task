from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class TokenRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class AnalysisResponse(BaseModel):
    sector: str
    generated_at: datetime
    report: str  # Markdown content


class SessionInfo(BaseModel):
    session_id: str
    username: str
    requests_made: int
    last_request: Optional[datetime] = None


class ErrorResponse(BaseModel):
    detail: str
    error_code: str
