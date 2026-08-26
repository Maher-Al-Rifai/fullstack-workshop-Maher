"""Unit tests for slug normalization edge cases."""

import pytest

from app.repositories.project_repository import _slugify


@pytest.mark.parametrize(
    "name, expected",
    [
        ("My Project", "my-project"),
        ("  leading and trailing  ", "leading-and-trailing"),
        ("Hello---World", "hello-world"),  # consecutive special chars collapse
        ("Café & Co.", "caf-co"),  # non-ASCII stripped
        ("123 Numbers First", "123-numbers-first"),
        ("ALL CAPS", "all-caps"),
        ("snake_case_name", "snake-case-name"),  # underscores become hyphens
        ("already-slug", "already-slug"),
        ("a" * 100, "a" * 100),  # long names pass through
    ],
)
def test_slugify_produces_expected_output(name: str, expected: str) -> None:
    assert _slugify(name) == expected


@pytest.mark.parametrize(
    "name",
    [
        "---",  # all special chars → stripped to "" → fallback to "project"
        "!!!",
        "   ",
    ],
)
def test_slugify_all_special_chars_falls_back_to_project(name: str) -> None:
    assert _slugify(name) == "project"


def test_slugify_output_contains_only_allowed_chars() -> None:
    result = _slugify("Hello World! @#$ 2025")
    assert all(c.isalnum() or c == "-" for c in result)
