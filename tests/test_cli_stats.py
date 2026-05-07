"""Tests for envdiff.cli_stats."""
import json
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

from envdiff.cli_stats import run_stats


@pytest.fixture()
def dev_env_file(tmp_path: Path) -> str:
    p = tmp_path / ".env.dev"
    p.write_text(textwrap.dedent("""\
        APP_NAME=myapp
        DEBUG=true
        PORT=8000
        SECRET_KEY=abc123
    """))
    return str(p)


@pytest.fixture()
def prod_env_file(tmp_path: Path) -> str:
    p = tmp_path / ".env.prod"
    p.write_text(textwrap.dedent("""\
        APP_NAME=myapp
        DEBUG=false
        PORT=80
    """))
    return str(p)


def _args(files, fmt="text", fail_below=None):
    return SimpleNamespace(files=files, fmt=fmt, fail_below=fail_below)


def test_text_output_contains_totals(dev_env_file, prod_env_file, capsys):
    run_stats(_args([dev_env_file, prod_env_file]))
    out = capsys.readouterr().out
    assert "Total keys" in out
    assert "Health ratio" in out


def test_json_output_is_valid(dev_env_file, prod_env_file, capsys):
    run_stats(_args([dev_env_file, prod_env_file], fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "total_keys" in data
    assert "health_ratio" in data


def test_json_contains_environments(dev_env_file, prod_env_file, capsys):
    run_stats(_args([dev_env_file, prod_env_file], fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert len(data["environments"]) == 2


def test_fail_below_exits_one_when_unhealthy(dev_env_file, prod_env_file):
    """With a missing key the health ratio should be < 1.0."""
    with pytest.raises(SystemExit) as exc_info:
        run_stats(_args([dev_env_file, prod_env_file], fail_below=1.0))
    assert exc_info.value.code == 1


def test_fail_below_no_exit_when_healthy(tmp_path, capsys):
    p1 = tmp_path / "a.env"
    p2 = tmp_path / "b.env"
    p1.write_text("KEY=val\n")
    p2.write_text("KEY=val\n")
    # Should NOT raise SystemExit
    run_stats(_args([str(p1), str(p2)], fail_below=0.5))


def test_too_few_files_exits(capsys):
    with pytest.raises(SystemExit) as exc_info:
        run_stats(_args(["only_one.env"]))
    assert exc_info.value.code == 2
