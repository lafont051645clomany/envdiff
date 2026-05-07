"""Tests for envdiff.comparator_stats."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.comparator_stats import (
    ComparisonStats,
    compute_stats,
    stats_to_dict,
)


@pytest.fixture()
def clean_diff() -> DiffResult:
    return DiffResult(
        missing_keys=[],
        mismatched_keys=[],
        matching_keys=["APP_NAME", "DEBUG", "PORT"],
    )


@pytest.fixture()
def mixed_diff() -> DiffResult:
    return DiffResult(
        missing_keys=["SECRET_KEY"],
        mismatched_keys=["DATABASE_URL"],
        matching_keys=["APP_NAME"],
    )


def test_health_ratio_perfect(clean_diff):
    stats = compute_stats(clean_diff, ["dev", "prod"])
    assert stats.health_ratio == 1.0


def test_health_ratio_partial(mixed_diff):
    stats = compute_stats(mixed_diff, ["dev", "prod"])
    assert 0.0 < stats.health_ratio < 1.0


def test_total_keys_counts_all_categories(mixed_diff):
    stats = compute_stats(mixed_diff, ["dev", "prod"])
    assert stats.total_keys == 3  # missing + mismatch + matching


def test_problem_count_is_sum(mixed_diff):
    stats = compute_stats(mixed_diff, ["dev", "prod"])
    assert stats.problem_count == stats.missing_count + stats.mismatch_count


def test_environments_stored(clean_diff):
    stats = compute_stats(clean_diff, ["dev", "staging", "prod"])
    assert stats.environments == ["dev", "staging", "prod"]


def test_empty_diff_no_crash():
    diff = DiffResult(missing_keys=[], mismatched_keys=[], matching_keys=[])
    stats = compute_stats(diff, ["dev"])
    assert stats.total_keys == 0
    assert stats.health_ratio == 1.0


def test_stats_to_dict_keys(mixed_diff):
    stats = compute_stats(mixed_diff, ["dev", "prod"])
    d = stats_to_dict(stats)
    expected_keys = {
        "total_keys", "missing_count", "mismatch_count",
        "matching_count", "health_ratio", "problem_count",
        "environments", "coverage",
    }
    assert expected_keys == set(d.keys())


def test_stats_to_dict_health_ratio_rounded(mixed_diff):
    stats = compute_stats(mixed_diff, ["dev", "prod"])
    d = stats_to_dict(stats)
    assert isinstance(d["health_ratio"], float)
    assert 0.0 <= d["health_ratio"] <= 1.0


def test_coverage_keys_match_env_names(clean_diff):
    stats = compute_stats(clean_diff, ["dev", "prod"])
    assert set(stats.coverage.keys()) == {"dev", "prod"}


def test_matching_count_correct(clean_diff):
    stats = compute_stats(clean_diff, ["dev"])
    assert stats.matching_count == 3
