"""Tests for envdiff.interpolator."""

import pytest
from envdiff.interpolator import (
    InterpolationResult,
    find_references,
    interpolate_env,
)


# ---------------------------------------------------------------------------
# find_references
# ---------------------------------------------------------------------------

def test_find_references_brace_syntax():
    assert find_references("${HOST}:${PORT}") == ["HOST", "PORT"]


def test_find_references_dollar_syntax():
    assert find_references("$HOST:$PORT") == ["HOST", "PORT"]


def test_find_references_no_refs():
    assert find_references("plain-value") == []


def test_find_references_mixed():
    refs = find_references("${PROTO}://$HOST")
    assert "PROTO" in refs
    assert "HOST" in refs


# ---------------------------------------------------------------------------
# interpolate_env
# ---------------------------------------------------------------------------

def test_simple_interpolation():
    env = {"HOST": "localhost", "URL": "http://${HOST}/api"}
    result = interpolate_env(env)
    assert result.resolved["URL"] == "http://localhost/api"


def test_no_references_unchanged():
    env = {"KEY": "value", "OTHER": "static"}
    result = interpolate_env(env)
    assert result.resolved == env
    assert not result.has_unresolved


def test_unresolved_ref_tracked():
    env = {"URL": "http://${MISSING_HOST}/path"}
    result = interpolate_env(env)
    assert "URL" in result.unresolved_refs
    assert "MISSING_HOST" in result.unresolved_refs["URL"]
    assert result.has_unresolved


def test_chained_interpolation():
    env = {
        "PROTO": "https",
        "HOST": "example.com",
        "BASE": "${PROTO}://${HOST}",
        "URL": "${BASE}/api",
    }
    result = interpolate_env(env)
    assert result.resolved["BASE"] == "https://example.com"
    assert result.resolved["URL"] == "https://example.com/api"


def test_changed_keys_reported():
    env = {"HOST": "localhost", "DSN": "postgres://${HOST}/db"}
    result = interpolate_env(env)
    assert "DSN" in result.changed_keys
    assert "HOST" not in result.changed_keys


def test_circular_reference_does_not_hang():
    # A -> B -> A should not recurse infinitely
    env = {"A": "${B}", "B": "${A}"}
    result = interpolate_env(env)  # must return without error
    assert isinstance(result, InterpolationResult)


def test_original_preserved():
    env = {"HOST": "localhost", "URL": "${HOST}:5432"}
    result = interpolate_env(env)
    assert result.original["URL"] == "${HOST}:5432"
    assert result.resolved["URL"] == "localhost:5432"
