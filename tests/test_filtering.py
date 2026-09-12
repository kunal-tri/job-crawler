from app.config import Settings
from app.filtering import assess
from app.models import Job


def settings() -> Settings:
    return Settings(None, None, None, 800_000, True, False, 2, "IN", (), True, 50, __import__("pathlib").Path("state.json"))


def test_entry_role_with_8_lpa_qualifies() -> None:
    job = Job("test", "1", "Software Engineer", "Example", "https://example.test/1", description="Graduate role, 0-1 years", salary_min_inr=800_000)
    result = assess(job, settings())
    assert result.qualifies
    assert result.fresher_score >= 35


def test_low_salary_rejected_in_strict_mode() -> None:
    job = Job("test", "2", "Intern", "Example", "https://example.test/2", description="Internship", salary_min_inr=799_999)
    assert assess(job, settings()).rejection_reason == "salary does not qualify"


def test_senior_role_rejected() -> None:
    job = Job("test", "3", "Senior Engineer", "Example", "https://example.test/3", salary_min_inr=1_000_000)
    assert assess(job, settings()).rejection_reason == "senior role"

