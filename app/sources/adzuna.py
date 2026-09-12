from __future__ import annotations

import json
import logging
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from app.config import Settings
from app.models import Job

LOG = logging.getLogger(__name__)


class AdzunaSource:
    """Official Adzuna API adapter; it does not scrape job boards."""

    name = "adzuna"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def enabled(self) -> bool:
        return bool(self.settings.adzuna_app_id and self.settings.adzuna_app_key)

    def discover_jobs(self, query: str) -> list[Job]:
        if not self.enabled:
            return []
        params = urlencode({
            "app_id": self.settings.adzuna_app_id,
            "app_key": self.settings.adzuna_app_key,
            "results_per_page": self.settings.max_results_per_query,
            "what": query,
            "content-type": "application/json",
        })
        url = f"https://api.adzuna.com/v1/api/jobs/{self.settings.target_country.lower()}/search/1?{params}"
        request = Request(url, headers={"Accept": "application/json", "User-Agent": "job-hunter/1.0"})
        try:
            with urlopen(request, timeout=20) as response:  # nosec B310: fixed HTTPS API URL
                payload = json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            LOG.warning("Adzuna request failed for query %r: %s", query, exc)
            return []
        return [self._job(row) for row in payload.get("results", []) if row.get("redirect_url")]

    @staticmethod
    def _job(row: dict) -> Job:
        salary_min = row.get("salary_min")
        salary_max = row.get("salary_max")
        # India endpoint salary values are INR annual figures when provided by Adzuna.
        salary_text = None
        if salary_min is not None or salary_max is not None:
            salary_text = f"₹{salary_min or '?'}–₹{salary_max or '?'} / year (Adzuna)"
        return Job(
            source="adzuna",
            source_id=str(row.get("id", row.get("redirect_url"))),
            title=row.get("title", "Untitled"),
            company=(row.get("company") or {}).get("display_name", "Unknown company"),
            url=row["redirect_url"],
            location=(row.get("location") or {}).get("display_name", "Unknown"),
            description=row.get("description", ""),
            published_at=row.get("created"),
            salary_min_inr=int(salary_min) if salary_min else None,
            salary_max_inr=int(salary_max) if salary_max else None,
            salary_text=salary_text,
        )

