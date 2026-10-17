"""The project config as a model (`.rb_semkit/config.toml`): the name, the provider, the output, the CLI version it needs,
`lists`, the folders of the Human's word lists, and `models.dir`, the folder of the encoders. A field has a default, so
an old config still loads.

A field's description is the format `config set` accepts for it; `value` and `with_value` read and set a dotted key.
"""

from __future__ import annotations

import json
from typing import Annotated

from packaging.version import Version
from pydantic import AfterValidator, BaseModel, Field
from pydantic.fields import FieldInfo

from .errors import InvalidArguments

TEXT = "any text"


class ProviderConfig(BaseModel):
    name: str = Field("default", description=TEXT)


class OutputConfig(BaseModel):
    format: str = Field("human", description=TEXT)


def _version(text: str) -> str:
    Version(text)  # InvalidVersion is a ValueError: the model refuses the text
    return text


class ModelsConfig(BaseModel):
    dir: str = Field(
        "",
        description="the folder of the encoders, as /abs/models or ~/models; a relative one is from the project; empty:"
        " the system cache",
    )


class CliCompat(BaseModel):
    min_version: Annotated[str, AfterValidator(_version)] = Field("0.1.0", description="a version, as 0.2.0")


class ProjectConfig(BaseModel):
    version: int = Field(1, description="a whole number, as 1")
    name: str = Field(description=TEXT)
    lists: list[str] = Field(
        default_factory=list,
        description='a JSON list of folders of word lists, as ["/abs/lists", "~/lists"]; a relative one is from the project',
    )
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    cli: CliCompat = Field(default_factory=CliCompat)


def _fields(model: type[BaseModel] = ProjectConfig, prefix: str = "") -> dict[str, FieldInfo]:
    """Every key `config set` takes, dotted (cli.min_version), and its field."""
    found: dict[str, FieldInfo] = {}
    for name, field in model.model_fields.items():
        section = field.annotation
        if isinstance(section, type) and issubclass(section, BaseModel):
            found |= _fields(section, f"{prefix}{name}.")
        else:
            found[f"{prefix}{name}"] = field
    return found


def config_keys() -> list[str]:
    """Every key `config set` takes, dotted, in the order of the model."""
    return list(_fields())


def _unknown(key: str) -> InvalidArguments:
    return InvalidArguments(f"Unknown config key '{key}'; allowed: {', '.join(config_keys())}.")


def value(config: ProjectConfig, key: str) -> object:
    """The value of the dotted `key`: one field, or a section (cli) as a dict."""
    found: object = config.model_dump()
    for part in key.split("."):
        if not isinstance(found, dict) or part not in found:
            raise _unknown(key)
        found = found[part]
    return found


def with_value(config: ProjectConfig, key: str, text: str) -> ProjectConfig:
    """`config` with the dotted `key` set to `text`: as it is for a text field, as JSON for any other (1, ["/abs"])."""
    field = _fields().get(key)
    if field is None:
        raise _unknown(key)
    data = config.model_dump()
    *sections, last = key.split(".")
    target = data
    for part in sections:
        target = target[part]
    try:
        target[last] = text if field.annotation is str else json.loads(text)
        return ProjectConfig.model_validate(data)
    except ValueError as exc:  # bad JSON, or a value of another type: both are ValueError
        raise InvalidArguments(f"{key}: {text!r} is not valid; allowed: {field.description}.") from exc
