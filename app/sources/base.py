from __future__ import annotations

from typing import Protocol

from app.models import Job


class JobSource(Protocol):
    name: str

    def discover_jobs(self, query: str) -> list[Job]: ...

