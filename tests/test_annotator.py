"""Tests for envdiff.annotator module."""

import pytest
from envdiff.annotator import Annotation, annotate_env, annotate_all, _infer_type


@pytest.fixture
def sample_env():
    return {
        "APP_NAME": "myapp",
        "DEBUG": "true",
        "PORT": "8080",
        "RATIO": "0.5",
        "SECRET_KEY": "supersecret",
        "DB_PASSWORD": "",
        "TAGS": "a,b,c",
    }


def test_infer_type_boolean():
    assert _infer_type("true") == "boolean"
    assert _infer_type("False") == "boolean"


def test_infer_type_integer():
    assert _infer_type("42") == "integer"


def test_infer_type_float():
    assert _infer_type("3.14") == "float"


def test_infer_type_list():
    assert _infer_type("a,b,c") == "list"


def test_infer_type_string():
    assert _infer_type("hello") == "string"


def test_infer_type_null():
    assert _infer_type(None) == "null"


def test_annotate_env_returns_all_keys(sample_env):
    result = annotate_env(sample_env, source="dev")
    assert len(result) == len(sample_env)
    keys = {a.key for a in result}
    assert keys == set(sample_env.keys())


def test_annotate_env_source_set(sample_env):
    result = annotate_env(sample_env, source="staging")
    assert all(a.source == "staging" for a in result)


def test_annotate_env_secret_flagged(sample_env):
    result = annotate_env(sample_env, source="dev")
    secret_keys = {a.key for a in result if a.is_secret}
    assert "SECRET_KEY" in secret_keys
    assert "DB_PASSWORD" in secret_keys


def test_annotate_env_empty_flagged(sample_env):
    result = annotate_env(sample_env, source="dev")
    empty_keys = {a.key for a in result if a.is_empty}
    assert "DB_PASSWORD" in empty_keys
    assert "APP_NAME" not in empty_keys


def test_annotate_env_type_hints(sample_env):
    result = {a.key: a.type_hint for a in annotate_env(sample_env, source="dev")}
    assert result["DEBUG"] == "boolean"
    assert result["PORT"] == "integer"
    assert result["RATIO"] == "float"
    assert result["TAGS"] == "list"
    assert result["APP_NAME"] == "string"


def test_annotate_env_tags_include_secret(sample_env):
    result = annotate_env(sample_env, source="dev")
    secret_ann = next(a for a in result if a.key == "SECRET_KEY")
    assert "secret" in secret_ann.tags


def test_annotate_all_returns_dict():
    envs = {
        "dev": {"APP": "dev_app", "DEBUG": "true"},
        "prod": {"APP": "prod_app", "DEBUG": "false"},
    }
    result = annotate_all(envs)
    assert set(result.keys()) == {"dev", "prod"}
    assert len(result["dev"]) == 2
    assert len(result["prod"]) == 2


def test_annotate_all_empty_env():
    result = annotate_all({"dev": {}})
    assert result["dev"] == []
