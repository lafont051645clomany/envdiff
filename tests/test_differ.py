"""Tests for envdiff.differ module."""

import pytest
from envdiff.differ import (
    build_unified_diff,
    classify_keys,
    count_by_status,
    DIFF_ADDED,
    DIFF_REMOVED,
    DIFF_CHANGED,
    DIFF_UNCHANGED,
)


@pytest.fixture
def env_a():
    return {"APP_NAME": "myapp", "DEBUG": "true", "PORT": "8080"}


@pytest.fixture
def env_b():
    return {"APP_NAME": "myapp", "DEBUG": "false", "HOST": "localhost"}


def test_unified_diff_headers(env_a, env_b):
    lines = build_unified_diff(env_a, env_b, label_a="dev", label_b="prod")
    assert lines[0] == "--- dev"
    assert lines[1] == "+++ prod"


def test_unified_diff_removed_key(env_a, env_b):
    lines = build_unified_diff(env_a, env_b)
    assert "-PORT=8080" in lines


def test_unified_diff_added_key(env_a, env_b):
    lines = build_unified_diff(env_a, env_b)
    assert "+HOST=localhost" in lines


def test_unified_diff_changed_key(env_a, env_b):
    lines = build_unified_diff(env_a, env_b)
    assert "-DEBUG=true" in lines
    assert "+DEBUG=false" in lines


def test_unified_diff_unchanged_key(env_a, env_b):
    lines = build_unified_diff(env_a, env_b)
    assert " APP_NAME=myapp" in lines


def test_unified_diff_sorted_keys(env_a, env_b):
    lines = build_unified_diff(env_a, env_b)
    key_lines = [l for l in lines if l not in ("--- a", "+++ b")]
    keys = [l[1:].split("=")[0] for l in key_lines]
    assert keys == sorted(keys)


def test_classify_keys_added(env_a, env_b):
    result = classify_keys(env_a, env_b)
    assert result["HOST"] == DIFF_ADDED


def test_classify_keys_removed(env_a, env_b):
    result = classify_keys(env_a, env_b)
    assert result["PORT"] == DIFF_REMOVED


def test_classify_keys_changed(env_a, env_b):
    result = classify_keys(env_a, env_b)
    assert result["DEBUG"] == DIFF_CHANGED


def test_classify_keys_unchanged(env_a, env_b):
    result = classify_keys(env_a, env_b)
    assert result["APP_NAME"] == DIFF_UNCHANGED


def test_count_by_status(env_a, env_b):
    classification = classify_keys(env_a, env_b)
    counts = count_by_status(classification)
    assert counts[DIFF_ADDED] == 1
    assert counts[DIFF_REMOVED] == 1
    assert counts[DIFF_CHANGED] == 1
    assert counts[DIFF_UNCHANGED] == 1


def test_count_by_status_identical():
    env = {"KEY": "val"}
    counts = count_by_status(classify_keys(env, env))
    assert counts[DIFF_UNCHANGED] == 1
    assert counts[DIFF_ADDED] == 0
    assert counts[DIFF_REMOVED] == 0
    assert counts[DIFF_CHANGED] == 0
