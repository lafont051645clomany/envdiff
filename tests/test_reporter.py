"""Tests for envdiff.reporter."""

import json

import pytest

from envdiff.comparator import compare_envs
from envdiff.reporter import format_report


@pytest.fixture()
def env_dev() -> dict:
    return {"DB_HOST": "localhost", "DB_PASSWORD": "devpass", "DEBUG": "true"}


@pytest.fixture()
def env_prod() -> dict:
    return {"DB_HOST": "prod.db.example.com", "DB_PASSWORD": "s3cr3t", "LOG_LEVEL": "warn"}


@pytest.fixture()
def diff(env_dev, env_prod):
    return compare_envs([env_dev, env_prod])


# --- text format ---

def test_no_differences_message():
    env = {"KEY": "value"}
    diff = compare_envs([env, env])
    report = format_report(diff, ["dev", "prod"])
    assert "No differences found" in report


def test_text_report_contains_missing_section(diff):
    report = format_report(diff, ["dev", "prod"])
    assert "Missing Keys" in report


def test_text_report_missing_key_labels(diff):
    report = format_report(diff, ["dev", "prod"])
    # DEBUG only in dev → missing in prod; LOG_LEVEL only in prod → missing in dev
    assert "DEBUG" in report
    assert "LOG_LEVEL" in report


def test_text_report_contains_mismatch_section(diff):
    report = format_report(diff, ["dev", "prod"])
    assert "Mismatched Values" in report
    assert "DB_HOST" in report


def test_text_report_masks_secrets(diff, env_dev, env_prod):
    report = format_report(
        diff,
        ["dev", "prod"],
        mask_secrets=True,
        raw_envs=[env_dev, env_prod],
    )
    assert "devpass" not in report
    assert "s3cr3t" not in report
    assert "****" in report


def test_text_report_plain_values_visible(diff, env_dev, env_prod):
    report = format_report(
        diff,
        ["dev", "prod"],
        mask_secrets=False,
        raw_envs=[env_dev, env_prod],
    )
    assert "localhost" in report or "prod.db.example.com" in report


# --- json format ---

def test_json_report_structure(diff):
    raw = format_report(diff, ["dev", "prod"], output_format="json")
    data = json.loads(raw)
    assert "missing_keys" in data
    assert "mismatched_keys" in data


def test_json_report_missing_keys_content(diff):
    raw = format_report(diff, ["dev", "prod"], output_format="json")
    data = json.loads(raw)
    assert "DEBUG" in data["missing_keys"] or "LOG_LEVEL" in data["missing_keys"]


def test_json_report_mismatched_values(diff, env_dev, env_prod):
    raw = format_report(
        diff, ["dev", "prod"], output_format="json", raw_envs=[env_dev, env_prod]
    )
    data = json.loads(raw)
    assert "DB_HOST" in data["mismatched_keys"]
    entry = data["mismatched_keys"]["DB_HOST"]
    assert entry["dev"] == "localhost"
    assert entry["prod"] == "prod.db.example.com"


def test_json_report_masks_secrets(diff, env_dev, env_prod):
    raw = format_report(
        diff,
        ["dev", "prod"],
        mask_secrets=True,
        raw_envs=[env_dev, env_prod],
        output_format="json",
    )
    assert "devpass" not in raw
    assert "s3cr3t" not in raw
