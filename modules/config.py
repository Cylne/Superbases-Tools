from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


class ConfigError(RuntimeError):
    pass


@dataclass(frozen=True)
class Endpoint:
    name: str = "project"
    database_url: str = ""
    project_url: str = ""
    service_role_key: str = ""
    project_ref: str = ""
    access_token: str = ""


@dataclass(frozen=True)
class AppConfig:
    source: Endpoint
    target: Endpoint
    backup_dir: Path
    retention_count: int
    command_timeout: int
    storage_page_size: int
    functions_dir: Path
    telegram_bot_token: str
    telegram_chat_id: str


_ENV = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)(?::-([^}]*))?\}")


def _expand(value: Any) -> Any:
    if isinstance(value, str):

        def replace(match: re.Match[str]) -> str:
            key, default = match.group(1), match.group(2)
            result = os.getenv(key, default)

            if result is None:
                raise ConfigError(
                    f"environment variable {key} is required"
                )

            return result

        return _ENV.sub(replace, value)

    if isinstance(value, dict):
        return {k: _expand(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_expand(v) for v in value]

    return value


def _get_app_dir() -> Path:
    """
    Always resolve the application directory from the installed
    SupaMigrate source instead of the user's current working directory.
    """
    configured = os.getenv("SUPAMIGRATE_HOME")

    if configured:
        return Path(configured).expanduser().resolve()

    # modules/config.py -> project root
    return Path(__file__).resolve().parent.parent


def load_config(path: str | None = None) -> AppConfig:
    app_dir = _get_app_dir()

    # Load .env from the application directory.
    env_file = app_dir / ".env"
    if env_file.is_file():
        load_dotenv(env_file, override=False)

    # Explicit --config has highest priority.
    # Otherwise use SUPAMIGRATE_CONFIG.
    # Otherwise use config.json inside the application directory.
    if path:
        file = Path(path).expanduser().resolve()
    elif os.getenv("SUPAMIGRATE_CONFIG"):
        file = Path(os.environ["SUPAMIGRATE_CONFIG"]).expanduser().resolve()
    else:
        file = app_dir / "config.json"

    if not file.is_file():
        example = app_dir / "config.example.json"

        if example.is_file():
            raise ConfigError(
                f"configuration not found: {file}; "
                f"copy {example} to {file}"
            )

        raise ConfigError(f"configuration not found: {file}")

    try:
        raw = _expand(
            json.loads(file.read_text(encoding="utf-8"))
        )
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"invalid JSON in {file}: {exc}"
        ) from exc

    base = file.parent
    settings = raw.get("settings", {})
    telegram = raw.get("telegram", {})

    def endpoint(name: str) -> Endpoint:
        item = raw.get(name, {})

        return Endpoint(
            **{
                key: str(item.get(key, ""))
                for key in Endpoint.__dataclass_fields__
            }
        )

    return AppConfig(
        source=endpoint("source"),
        target=endpoint("target"),
        backup_dir=(
            base / settings.get("backup_dir", "backups")
        ).resolve(),
        retention_count=max(
            1,
            int(settings.get("retention_count", 10)),
        ),
        command_timeout=max(
            60,
            int(settings.get("command_timeout_seconds", 3600)),
        ),
        storage_page_size=min(
            1000,
            max(1, int(settings.get("storage_page_size", 100))),
        ),
        functions_dir=(
            base / settings.get(
                "functions_dir",
                "supabase/functions",
            )
        ).resolve(),
        telegram_bot_token=str(
            telegram.get("bot_token", "")
        ),
        telegram_chat_id=str(
            telegram.get("chat_id", "")
        ),
    )
