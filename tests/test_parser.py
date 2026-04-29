"""Tests for the envdiff.parser module."""

import pytest
from pathlib import Path

from envdiff.parser import parse_env_file, load_env_files, _strip_quotes


@pytest.fixture
def simple_env_file(tmp_path: Path) -> Path:
    content = """# Database config
DB_HOST=localhost
DB_PORT=5432
DB_NAME="mydb"
SECRET_KEY='supersecret'
EMPTY_VAR=
"""
    env_file = tmp_path / ".env"
    env_file.write_text(content)
    return env_file


@pytest.fixture
def invalid_env_file(tmp_path: Path) -> Path:
    content = "INVALID LINE WITHOUT EQUALS\n"
    env_file = tmp_path / ".env.invalid"
    env_file.write_text(content)
    return env_file


def test_parse_simple_env(simple_env_file: Path):
    result = parse_env_file(simple_env_file)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["DB_NAME"] == "mydb"
    assert result["SECRET_KEY"] == "supersecret"
    assert result["EMPTY_VAR"] == ""


def test_comments_ignored(simple_env_file: Path):
    result = parse_env_file(simple_env_file)
    assert "Database config" not in result
    assert len(result) == 5


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        parse_env_file("/nonexistent/.env")


def test_invalid_syntax_raises(invalid_env_file: Path):
    with pytest.raises(ValueError, match="Invalid syntax"):
        parse_env_file(invalid_env_file)


def test_strip_quotes():
    assert _strip_quotes('"hello"') == "hello"
    assert _strip_quotes("'world'") == "world"
    assert _strip_quotes("plain") == "plain"
    assert _strip_quotes("") == ""
    assert _strip_quotes('"single') == '"single'


def test_load_env_files(tmp_path: Path):
    f1 = tmp_path / ".env.dev"
    f1.write_text("FOO=bar\nBAZ=qux\n")
    f2 = tmp_path / ".env.prod"
    f2.write_text("FOO=prod_bar\n")

    result = load_env_files(f1, f2)
    assert ".env.dev" in result
    assert ".env.prod" in result
    assert result[".env.dev"]["FOO"] == "bar"
    assert result[".env.prod"]["FOO"] == "prod_bar"
