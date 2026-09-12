from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256


@dataclass(frozen=True)
class Job:
    source: str
    source_id: str
    title: str
    company: str
    url: str
    location: str = "Unknown"
    description: str = ""
    published_at: str | None = None
    salary_min_inr: int | None = None
    salary_max_inr: int | None = None
    salary_text: str | None = None

    @property
    def key(self) -> str:
        stable = f"{self.source}:{self.source_id or self.url}"
        return sha256(stable.encode()).hexdigest()[:24]

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class Assessment:
    job: Job
    fresher_score: int
    total_score: int
    experience_evidence: str
    salary_status: str
    qualifies: bool
    rejection_reason: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

