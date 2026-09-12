from app.salary import parse_inr_salary


def test_lpa_range() -> None:
    value = parse_inr_salary("Compensation ₹8–12 LPA")
    assert (value.minimum_inr, value.maximum_inr) == (800_000, 1_200_000)


def test_monthly_salary() -> None:
    value = parse_inr_salary("Rs. 60,000 per month")
    assert value.minimum_inr == 720_000


def test_unknown_salary() -> None:
    assert parse_inr_salary("competitive salary").minimum_inr is None

