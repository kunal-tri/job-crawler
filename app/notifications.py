from __future__ import annotations

import json
from urllib.request import Request, urlopen

from app.models import Assessment


def format_alert(items: list[Assessment]) -> str:
    lines = [f"🚨 {len(items)} new qualifying fresher jobs"]
    for index, item in enumerate(items, 1):
        job = item.job
        pay = job.salary_text or "Salary: unknown"
        lines.extend([
            f"\n{index}. {job.title} — {job.company}",
            f"📍 {job.location} | 💰 {pay}",
            f"🎓 {item.experience_evidence} | ⭐ {item.total_score}/100",
            f"Source: {job.source} | Apply: {job.url}",
        ])
    return "\n".join(lines)


def send_slack(webhook_url: str, items: list[Assessment]) -> None:
    payload = json.dumps({"text": format_alert(items)}).encode()
    request = Request(webhook_url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=15) as response:  # nosec B310: caller configures Slack HTTPS URL
        if not 200 <= response.status < 300:
            raise RuntimeError(f"Slack returned HTTP {response.status}")

