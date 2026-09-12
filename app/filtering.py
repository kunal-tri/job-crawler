from __future__ import annotations

import re

from app.config import Settings
from app.models import Assessment, Job

SENIOR = re.compile(r"\b(senior|staff|principal|lead|manager|director|head of)\b", re.I)
ENTRY = re.compile(r"\b(intern(ship)?|graduate|new grad|fresher|entry[ -]?level|trainee|associate|junior)\b", re.I)
ZERO_TO_ONE = re.compile(r"\b0\s*(?:-|–|to)\s*1\s*(?:years?|yrs?)\b|\bno experience\b", re.I)
ZERO_TO_TWO = re.compile(r"\b0\s*(?:-|–|to)\s*2\s*(?:years?|yrs?)\b", re.I)
EXPERIENCE = re.compile(r"\b(\d+)\s*\+?\s*(?:years?|yrs?)\b", re.I)


def assess(job: Job, settings: Settings) -> Assessment:
    text = f"{job.title} {job.description}"
    score = 0
    evidence: list[str] = []
    if ENTRY.search(text):
        score += 35
        evidence.append("entry-level wording")
    if ZERO_TO_ONE.search(text):
        score += 30
        evidence.append("0–1 years/no experience")
    elif ZERO_TO_TWO.search(text):
        score += 20
        evidence.append("0–2 years")
    max_mentioned = max((int(x) for x in EXPERIENCE.findall(text)), default=None)
    if SENIOR.search(text):
        score -= 60
        return Assessment(job, max(0, score), 0, "; ".join(evidence) or "senior wording", "unknown", False, "senior role")
    if max_mentioned is not None and max_mentioned > settings.max_experience_years:
        return Assessment(job, max(0, score - 50), 0, f"{max_mentioned}+ years", "unknown", False, "experience exceeds limit")

    if job.salary_min_inr is None:
        salary_status = "unknown"
        salary_ok = settings.include_unknown_salary or not settings.strict_salary_filter
    elif job.salary_min_inr >= settings.min_salary_inr:
        salary_status = "meets minimum"
        salary_ok = True
        score += 20
    else:
        salary_status = "below minimum"
        salary_ok = not settings.strict_salary_filter
    if not salary_ok:
        return Assessment(job, max(0, score), 0, "; ".join(evidence) or "no explicit fresher evidence", salary_status, False, "salary does not qualify")
    # score remains explainable and intentionally conservative for unknown experience.
    total = min(100, max(0, score + (10 if job.published_at else 0)))
    return Assessment(job, max(0, score), total, "; ".join(evidence) or "no explicit experience evidence", salary_status, True)

