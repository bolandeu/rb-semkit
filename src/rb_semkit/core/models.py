from __future__ import annotations

from pydantic import BaseModel, Field


class ProviderConfig(BaseModel):
    name: str = "default"


class OutputConfig(BaseModel):
    format: str = "human"


class CliCompat(BaseModel):
    min_version: str = "0.1.0"


class ProjectConfig(BaseModel):
    version: int = 1
    name: str
    lists: list[str] = Field(default_factory=list)  # folders of word lists: absolute, ~ or relative to the project
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    cli: CliCompat = Field(default_factory=CliCompat)
