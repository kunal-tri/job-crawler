from __future__ import annotations

import json
from pathlib import Path

from app.models import Assessment, utc_now


class StateStore:
    """Small portable state store suitable for a free scheduled GitHub Action."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.seen: dict[str, dict] = {}

    def load(self) -> None:
        if self.path.exists():
            self.seen = json.loads(self.path.read_text(encoding="utf-8")).get("jobs", {})

    def new(self, assessments: list[Assessment]) -> list[Assessment]:
        return [item for item in assessments if item.job.key not in self.seen]

    def record(self, assessments: list[Assessment]) -> None:
        for item in assessments:
            self.seen[item.job.key] = {
                "first_seen_at": utc_now(), "title": item.job.title,
                "company": item.job.company, "url": item.job.url,
            }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"jobs": self.seen}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

