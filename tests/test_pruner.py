"""Tests for envdiff.pruner."""
import pytest
from envdiff.pruner import PruneReport, prune_keys, prune_all


@pytest.fixture
def base_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "LEGACY_FLAG": "true",
        "EMPTY_KEY": "",
    }


@pytest.fixture
def reference():
    return {"DB_HOST", "DB_PORT", "EMPTY_KEY"}


# --- prune_keys ---

def test_prune_removes_key_not_in_reference(base_env, reference):
    report = prune_keys(base_env, reference)
    assert "LEGACY_FLAG" in report.removed_keys


def test_prune_retains_keys_in_reference(base_env, reference):
    report = prune_keys(base_env, reference)
    assert "DB_HOST" in report.pruned
    assert "DB_PORT" in report.pruned


def test_prune_reason_not_in_reference(base_env, reference):
    report = prune_keys(base_env, reference)
    assert report.reason["LEGACY_FLAG"] == "not_in_reference"


def test_prune_empty_false_keeps_empty_value(base_env, reference):
    report = prune_keys(base_env, reference, prune_empty=False)
    assert "EMPTY_KEY" in report.pruned


def test_prune_empty_true_removes_empty_value(base_env, reference):
    report = prune_keys(base_env, reference, prune_empty=True)
    assert "EMPTY_KEY" in report.removed_keys
    assert report.reason["EMPTY_KEY"] == "empty_value"


def test_has_removals_true(base_env, reference):
    report = prune_keys(base_env, reference)
    assert report.has_removals is True


def test_has_removals_false():
    env = {"A": "1"}
    report = prune_keys(env, {"A"})
    assert report.has_removals is False


def test_removal_count(base_env, reference):
    report = prune_keys(base_env, reference)
    assert report.removal_count == 1  # only LEGACY_FLAG


def test_removed_keys_sorted(base_env):
    ref = {"DB_HOST"}
    report = prune_keys(base_env, ref)
    assert report.removed_keys == sorted(report.removed_keys)


def test_original_env_unchanged(base_env, reference):
    original_copy = dict(base_env)
    prune_keys(base_env, reference)
    assert base_env == original_copy


def test_to_dict_keys(base_env, reference):
    report = prune_keys(base_env, reference, label="dev")
    d = report.to_dict()
    assert d["label"] == "dev"
    assert "removal_count" in d
    assert "removed_keys" in d
    assert "pruned_env" in d


# --- prune_all ---

def test_prune_all_returns_report_per_label():
    envs = {
        "dev": {"A": "1", "B": "2"},
        "prod": {"A": "1", "C": "3"},
    }
    reports = prune_all(envs, reference={"A", "B", "C"})
    assert set(reports.keys()) == {"dev", "prod"}


def test_prune_all_infers_union_reference():
    envs = {
        "dev": {"A": "1", "B": "2"},
        "prod": {"A": "1", "C": "3"},
    }
    # All keys are in the union — nothing should be pruned
    reports = prune_all(envs)
    for report in reports.values():
        assert not report.has_removals
