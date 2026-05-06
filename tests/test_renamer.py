"""Tests for envdiff.renamer."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.renamer import (
    RenameCandidate,
    RenameReport,
    detect_renames,
    format_rename_report,
)


@pytest.fixture()
def diff_with_rename_candidates() -> DiffResult:
    """A diff where DATABASE_URL was renamed to DB_URL."""
    return DiffResult(
        missing_keys={"DATABASE_URL", "SECRET_KEY"},
        extra_keys={"DB_URL", "SECRET_TOKEN"},
        mismatched_keys={},
    )


@pytest.fixture()
def diff_no_overlap() -> DiffResult:
    return DiffResult(
        missing_keys={"ALPHA"},
        extra_keys={"ZZZZ"},
        mismatched_keys={},
    )


@pytest.fixture()
def empty_diff() -> DiffResult:
    return DiffResult(missing_keys=set(), extra_keys=set(), mismatched_keys={})


def test_detect_renames_finds_close_match(diff_with_rename_candidates):
    report = detect_renames(diff_with_rename_candidates, threshold=0.5)
    keys = [(c.old_key, c.new_key) for c in report.candidates]
    assert ("DATABASE_URL", "DB_URL") in keys


def test_detect_renames_score_in_range(diff_with_rename_candidates):
    report = detect_renames(diff_with_rename_candidates, threshold=0.0)
    for candidate in report.candidates:
        assert 0.0 <= candidate.score <= 1.0


def test_detect_renames_respects_threshold(diff_no_overlap):
    report = detect_renames(diff_no_overlap, threshold=0.9)
    assert not report.has_candidates


def test_detect_renames_empty_diff(empty_diff):
    report = detect_renames(empty_diff)
    assert not report.has_candidates
    assert report.candidates == []


def test_rename_report_above_threshold(diff_with_rename_candidates):
    report = detect_renames(diff_with_rename_candidates, threshold=0.0)
    strong = report.above_threshold(0.99)
    for c in strong:
        assert c.score >= 0.99


def test_rename_candidate_label():
    c = RenameCandidate(old_key="FOO", new_key="BAR", score=0.85)
    assert "FOO" in c.label
    assert "BAR" in c.label
    assert "85%" in c.label


def test_format_rename_report_with_candidates(diff_with_rename_candidates):
    report = detect_renames(diff_with_rename_candidates, threshold=0.5)
    text = format_rename_report(report, threshold=0.5)
    assert "Possible renames" in text
    assert "->" in text


def test_format_rename_report_no_candidates(diff_no_overlap):
    report = detect_renames(diff_no_overlap, threshold=0.99)
    text = format_rename_report(report)
    assert "No rename candidates" in text


def test_candidates_sorted_by_score_descending(diff_with_rename_candidates):
    report = detect_renames(diff_with_rename_candidates, threshold=0.0)
    scores = [c.score for c in report.candidates]
    assert scores == sorted(scores, reverse=True)
