"""Salary parsing helpers for future ATS adapters and imported job descriptions."""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedSalary:
    minimum_inr: int | None
    maximum_inr: int | None
    period: str | None
    confidence: str


LPA = re.compile(r"(?:₹|rs\.?\s*)?(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?\s*(?:per\s*)?annum)", re.I)
ONE_LPA = re.compile(r"(?:₹|rs\.?\s*)?(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?\s*(?:per\s*)?annum)", re.I)
MONTHLY = re.compile(r"(?:₹|rs\.?\s*)([\d,]+)\s*(?:/|per\s*)month", re.I)
ANNUAL = re.compile(r"(?:₹|rs\.?\s*)([\d,]+)\s*(?:/|per\s*)?(?:year|annum|pa)\b", re.I)


def parse_inr_salary(text: str) -> ParsedSalary:
    """Parse explicit INR amounts only; never assume a salary from prose."""
    if match := LPA.search(text):
        return ParsedSalary(int(float(match.group(1)) * 100_000), int(float(match.group(2)) * 100_000), "year", "explicit")
    if match := ONE_LPA.search(text):
        value = int(float(match.group(1)) * 100_000)
        return ParsedSalary(value, value, "year", "explicit")
    if match := MONTHLY.search(text):
        value = int(match.group(1).replace(",", "")) * 12
        return ParsedSalary(value, value, "year", "explicit-monthly")
    if match := ANNUAL.search(text):
        value = int(match.group(1).replace(",", ""))
        return ParsedSalary(value, value, "year", "explicit")
    return ParsedSalary(None, None, None, "unknown")

