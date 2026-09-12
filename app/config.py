from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc


@dataclass(frozen=True)
class Settings:
    adzuna_app_id: str | None
    adzuna_app_key: str | None
    slack_webhook_url: str | None
    min_salary_inr: int
    strict_salary_filter: bool
    include_unknown_salary: bool
    max_experience_years: int
    target_country: str
    target_cities: tuple[str, ...]
    remote_allowed: bool
    max_results_per_query: int
    state_file: Path

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            adzuna_app_id=os.getenv("ADZUNA_APP_ID") or None,
            adzuna_app_key=os.getenv("ADZUNA_APP_KEY") or None,
            slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL") or None,
            min_salary_inr=_int("MIN_SALARY_INR", 800_000),
            strict_salary_filter=_bool("STRICT_SALARY_FILTER", True),
            include_unknown_salary=_bool("INCLUDE_UNKNOWN_SALARY", False),
            max_experience_years=_int("MAX_EXPERIENCE_YEARS", 2),
            target_country=os.getenv("TARGET_COUNTRY", "IN").upper(),
            target_cities=tuple(x.strip() for x in os.getenv("TARGET_CITIES", "").split(",") if x.strip()),
            remote_allowed=_bool("REMOTE_ALLOWED", True),
            max_results_per_query=_int("MAX_RESULTS_PER_QUERY", 50),
            state_file=Path(os.getenv("STATE_FILE", ".state/job_state.json")),
        )

