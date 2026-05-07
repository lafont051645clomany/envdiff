"""Tests for envdiff.cli_tag."""
import json
import pytest
from unittest.mock import patch, MagicMock
from envdiff.cli_tag import run_tag, _format_text, add_tag_subparser
from envdiff.tagger import TagReport


class _Args:
    def __init__(self, files, fmt="text", show_untagged=False):
        self.files = files
        self.fmt = fmt
        self.show_untagged = show_untagged


@pytest.fixture
def env_file(tmp_path):
    f = tmp_path / ".env"
    f.write_text(
        "DB_HOST=localhost\nJWT_SECRET=abc\nAPP_NAME=myapp\nLOG_LEVEL=debug\n"
    )
    return str(f)


def test_run_tag_text_output(env_file, capsys):
    args = _Args(files=[env_file])
    run_tag(args)
    captured = capsys.readouterr()
    assert "[database]" in captured.out or "[auth]" in captured.out or "[logging]" in captured.out


def test_run_tag_json_output(env_file, capsys):
    args = _Args(files=[env_file], fmt="json")
    run_tag(args)
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert env_file in data
    assert "tags" in data[env_file]
    assert "untagged" in data[env_file]


def test_run_tag_show_untagged(env_file, capsys):
    args = _Args(files=[env_file], show_untagged=True)
    run_tag(args)
    captured = capsys.readouterr()
    # APP_NAME should be untagged and shown
    assert "APP_NAME" in captured.out


def test_run_tag_file_not_found(capsys):
    args = _Args(files=["/nonexistent/.env"])
    with pytest.raises(SystemExit) as exc:
        run_tag(args)
    assert exc.value.code == 1


def test_format_text_no_keys():
    report = TagReport()
    result = _format_text(report, "test", show_untagged=False)
    assert "(no keys)" in result


def test_format_text_with_tags():
    report = TagReport(tags={"database": ["DB_HOST"]}, untagged=["APP_NAME"])
    result = _format_text(report, "dev", show_untagged=False)
    assert "[database]" in result
    assert "DB_HOST" in result
    assert "APP_NAME" not in result


def test_format_text_show_untagged():
    report = TagReport(tags={}, untagged=["APP_NAME"])
    result = _format_text(report, "dev", show_untagged=True)
    assert "[untagged]" in result
    assert "APP_NAME" in result


def test_add_tag_subparser():
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    add_tag_subparser(sub)
    args = parser.parse_args(["tag", "some.env"])
    assert args.fmt == "text"
    assert args.show_untagged is False
