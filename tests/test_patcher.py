"""Tests for envdiff.patcher."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.patcher import PatchEntry, PatchReport, build_patch, patch_to_dict


@pytest.fixture()
def diff_with_gaps() -> DiffResult:
    source = {"DB_HOST": "prod-db", "DB_PORT": "5432", "API_KEY": "secret"}
    target = {"DB_HOST": "localhost", "DEBUG": "true"}
    return DiffResult(
        source=source,
        target=target,
        missing_keys=["DB_PORT", "API_KEY"],
        extra_keys=["DEBUG"],
        mismatched_keys={"DB_HOST": ("prod-db", "localhost")},
    )


# ---------------------------------------------------------------------------
# PatchEntry.label
# ---------------------------------------------------------------------------

def test_patch_entry_label_add():
    e = PatchEntry(key="FOO", action="add", new_value="bar")
    assert e.label == "+ FOO=bar"


def test_patch_entry_label_update():
    e = PatchEntry(key="FOO", action="update", old_value="old", new_value="new")
    assert "~" in e.label
    assert "old" in e.label
    assert "new" in e.label


def test_patch_entry_label_remove():
    e = PatchEntry(key="FOO", action="remove", old_value="val")
    assert e.label.startswith("- FOO")


# ---------------------------------------------------------------------------
# build_patch – basic behaviour
# ---------------------------------------------------------------------------

def test_build_patch_adds_missing_keys(diff_with_gaps):
    report = build_patch(diff_with_gaps, "prod", "dev")
    add_keys = {e.key for e in report.by_action("add")}
    assert "DB_PORT" in add_keys
    assert "API_KEY" in add_keys


def test_build_patch_updates_mismatched_keys(diff_with_gaps):
    report = build_patch(diff_with_gaps, "prod", "dev")
    update_keys = {e.key for e in report.by_action("update")}
    assert "DB_HOST" in update_keys


def test_build_patch_no_removals_by_default(diff_with_gaps):
    report = build_patch(diff_with_gaps, "prod", "dev")
    assert report.by_action("remove") == []


def test_build_patch_removals_when_requested(diff_with_gaps):
    report = build_patch(diff_with_gaps, "prod", "dev", include_removals=True)
    remove_keys = {e.key for e in report.by_action("remove")}
    assert "DEBUG" in remove_keys


def test_build_patch_entries_sorted(diff_with_gaps):
    report = build_patch(diff_with_gaps, "prod", "dev")
    keys = [e.key for e in report.entries]
    assert keys == sorted(keys)


def test_build_patch_labels(diff_with_gaps):
    report = build_patch(diff_with_gaps, "prod", "dev")
    assert report.source_label == "prod"
    assert report.target_label == "dev"


# ---------------------------------------------------------------------------
# PatchReport helpers
# ---------------------------------------------------------------------------

def test_patch_report_has_patches(diff_with_gaps):
    report = build_patch(diff_with_gaps, "prod", "dev")
    assert report.has_patches is True


def test_patch_report_no_patches_on_identical():
    source = {"KEY": "val"}
    diff = DiffResult(
        source=source,
        target=source.copy(),
        missing_keys=[],
        extra_keys=[],
        mismatched_keys={},
    )
    report = build_patch(diff, "a", "b")
    assert report.has_patches is False
    assert report.count == 0


# ---------------------------------------------------------------------------
# patch_to_dict
# ---------------------------------------------------------------------------

def test_patch_to_dict_structure(diff_with_gaps):
    report = build_patch(diff_with_gaps, "prod", "dev")
    d = patch_to_dict(report)
    assert d["source"] == "prod"
    assert d["target"] == "dev"
    assert isinstance(d["entries"], list)
    assert d["count"] == len(d["entries"])


def test_patch_to_dict_entry_keys(diff_with_gaps):
    report = build_patch(diff_with_gaps, "prod", "dev")
    entry = patch_to_dict(report)["entries"][0]
    assert {"key", "action", "old_value", "new_value"} == set(entry.keys())
