from __future__ import annotations

import argparse
import logging
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor

from app.config import Settings
from app.filtering import assess
from app.notifications import format_alert, send_slack
from app.sources import AdzunaSource
from app.storage import StateStore

QUERIES = ("software engineer", "data analyst", "machine learning", "devops", "qa engineer", "business development")


def run(dry_run: bool = False) -> int:
    settings = Settings.from_env()
    source = AdzunaSource(settings)
    if not source.enabled:
        logging.error("Adzuna is disabled: configure ADZUNA_APP_ID and ADZUNA_APP_KEY.")
        return 2
    jobs = OrderedDict()
    # Adzuna's documented per-minute quota is well above this bounded fan-out;
    # limiting it to three workers avoids one slow query blocking a whole cycle.
    with ThreadPoolExecutor(max_workers=3) as executor:
        batches = executor.map(source.discover_jobs, QUERIES)
        for batch in batches:
            for job in batch:
                jobs.setdefault(job.key, job)
    assessments = [assess(job, settings) for job in jobs.values()]
    qualifying = [item for item in assessments if item.qualifies]
    store = StateStore(settings.state_file)
    store.load()
    new_items = store.new(qualifying)
    print(f"discovered={len(jobs)} qualifying={len(qualifying)} new={len(new_items)}")
    if new_items:
        print(format_alert(new_items))
        if not dry_run and settings.slack_webhook_url:
            send_slack(settings.slack_webhook_url, new_items)
    # Never mark alerts delivered before a Slack failure, or while notifications
    # are not configured. This allows a later Slack setup to receive the backlog.
    if not dry_run and settings.slack_webhook_url:
        store.record(qualifying)
    if not settings.slack_webhook_url and not dry_run:
        logging.warning("SLACK_WEBHOOK_URL is unset; no notification sent.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover fresher-friendly jobs via compliant APIs.")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and score jobs without alerts or state updates")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(run(args.dry_run))
