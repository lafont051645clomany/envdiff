"""Tests for envdiff.cli_template."""

import textwrap
from pathlib import Path

import pytest

from envdiff.cli_template import run_template


@pytest.fixture
def env_file(tmp_path: Path) -> Path:
    p = tmp_path / ".env"
    p.write_text(
        textwrap.dedent(
            """\
            APP_NAME=myapp
            DB_PASSWORD=supersecret
            PORT=8080
            """
        )
    )
    return p


class FakeArgs:
    def __init__(self, env_file, output=None, no_comments=False):
        self.env_file = str(env_file)
        self.output = output
        self.no_comments = no_comments


def test_run_template_stdout(env_file, capsys):
    args = FakeArgs(env_file)
    rc = run_template(args)
    assert rc == 0
    captured = capsys.readouterr()
    assert "APP_NAME=<app_name>" in captured.out
    assert "DB_PASSWORD=<secret>" in captured.out
    assert "PORT=<port>" in captured.out


def test_run_template_no_original_values(env_file, capsys):
    args = FakeArgs(env_file)
    run_template(args)
    captured = capsys.readouterr()
    assert "supersecret" not in captured.out
    assert "myapp" not in captured.out


def test_run_template_with_comments(env_file, capsys):
    args = FakeArgs(env_file, no_comments=False)
    run_template(args)
    captured = capsys.readouterr()
    assert "# secret" in captured.out


def test_run_template_no_comments(env_file, capsys):
    args = FakeArgs(env_file, no_comments=True)
    run_template(args)
    captured = capsys.readouterr()
    assert "# secret" not in captured.out


def test_run_template_writes_file(env_file, tmp_path):
    out = tmp_path / "out" / ".env.example"
    args = FakeArgs(env_file, output=str(out))
    rc = run_template(args)
    assert rc == 0
    assert out.exists()
    content = out.read_text()
    assert "DB_PASSWORD=<secret>" in content


def test_run_template_missing_file(tmp_path, capsys):
    args = FakeArgs(tmp_path / "nonexistent.env")
    rc = run_template(args)
    assert rc == 1
    captured = capsys.readouterr()
    assert "not found" in captured.err
