from typing import Literal

from pydantic import BaseModel, Field


class AIImproveRequest(BaseModel):
    action: Literal["summary", "experience"]
    content: str = Field(..., min_length=10)


class ResumeDownloadRequest(BaseModel):
    template_slug: str
    full_name: str
    email: str
    phone: str = ""
    location: str = ""
    summary: str = ""
    skills: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
