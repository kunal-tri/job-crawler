# Job Hunter

A small job-discovery worker that uses the official Adzuna API, scores fresher-friendly India roles, applies a strict ₹8 LPA minimum where salary is explicit, de-duplicates results, and can alert a Slack incoming-webhook channel.

It intentionally does **not** scrape LinkedIn, automate a browser, use LinkedIn credentials, or bypass access controls. The one configured source is Adzuna; additional ATS sources need an authorized company/board list or credentials before they can discover useful jobs.

## What is included

- Official Adzuna API adapter with graceful credential handling.
- Explainable fresher/experience filter, strict salary threshold, duplicate state, Slack batch formatter, and dry-run mode.
- A free GitHub Actions schedule (every six hours) that persists non-secret de-duplication state in the repository.
- Docker configuration for local execution.

This is a best-effort scheduled worker, not an always-on server. GitHub can delay cron jobs. A private GitHub Free repository includes a monthly Actions allowance; this schedule should be modest, but workflows stop if the allowance is exhausted and there is no payment method. Public repositories have free standard-runner usage, but make all code and crawl state public.

## Local setup

1. Copy `.env.example` to `.env` and fill `ADZUNA_APP_ID` and `ADZUNA_APP_KEY`. Keep `.env` private.
2. Optionally add `SLACK_WEBHOOK_URL`.
3. Run `python -m app.main --dry-run` from this directory, or `docker compose up --build`.

Without a Slack webhook, normal mode will discover and print jobs but deliberately will not record them as delivered, so no jobs are lost before notifications are configured.

## GitHub deployment: no payment method

Create a GitHub repository (private is the safer default), push this project, then add these repository secrets under `Settings → Secrets and variables → Actions`:

| Secret | Required | Meaning |
| --- | --- | --- |
| `ADZUNA_APP_ID` | Yes | Your existing Adzuna application ID |
| `ADZUNA_APP_KEY` | Yes | Your existing Adzuna application key |
| `SLACK_WEBHOOK_URL` | To receive alerts | Incoming-webhook URL for the target Slack channel |

The committed workflow calls the official API every six hours, sends only newly discovered qualifying jobs, and commits `.state/job_state.json` after a successful Slack run. Use **Actions → Scheduled job discovery → Run workflow** with dry-run first. Never enter any secret into a source file or commit message.

No host can honestly guarantee a free forever 24×7 service without account/service limits. GitHub's free tier currently includes 2,000 monthly minutes for private repositories, while standard runners are free in public repositories; verify the current entitlement in GitHub before relying on it.

## Configuration

The defaults are India, ₹800,000/year, strict salary filtering, and up to two years' experience. See `.env.example` for all options. Unknown salaries are excluded by default because the worker never claims an unlisted salary meets the requirement.

## Verification

Run `python -m pytest -q` after installing `requirements-dev.txt`. The tests do not call live APIs.
