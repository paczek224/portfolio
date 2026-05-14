from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    llm_provider: str
    llm_base_url: str
    llm_model: str
    llm_api_key: str | None
    project_root: Path


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_settings(project_root: Path) -> Settings:
    load_dotenv(project_root / ".env")

    return Settings(
        llm_provider=os.getenv("LLM_PROVIDER", "ollama"),
        llm_base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434"),
        llm_model=os.getenv("LLM_MODEL", "qwen3.6"),
        llm_api_key=os.getenv("LLM_API_KEY") or None,
        project_root=project_root,
    )
