"""Tests for the envdiff CLI module."""

import json
import textwrap
from pathlib import Path

import pytest

from envdiff.cli import run


@pytest.fixture()
def dev_env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env.dev"
    f.write_text(
        textwrap.dedent(
            """\
            APP_NAME=myapp
            DEBUG=true
            SECRET_KEY=dev-secret
            DATABASE_URL=postgres://localhost/dev
            """
        )
    )
    return f


@pytest.fixture()
def prod_env_file(tmp_path: Path) -> Path:
    f = tmp_path / ".env.prod"
    f.write_text(
        textwrap.dedent(
            """\
            APP_NAME=myapp
            SECRET_KEY=prod-secret
            DATABASE_URL=postgres://prod-host/prod
            """
        )
    )
    return f


def test_exit_code_zero_no_differences(tmp_path: Path) -> None:
    f1 = tmp_path / "a.env"
    f2 = tmp_path / "b.env"
    f1.write_text("KEY=value\n")
    f2.write_text("KEY=value\n")
    assert run([str(f1), str(f2), "--exit-code"]) == 0


def test_exit_code_one_with_differences(
    dev_env_file: Path, prod_env_file: Path
) -> None:
    result = run([str(dev_env_file), str(prod_env_file), "--exit-code"])
    assert result == 1


def test_exit_code_zero_without_flag(
    dev_env_file: Path, prod_env_file: Path
) -> None:
    result = run([str(dev_env_file), str(prod_env_file)])
    assert result == 0


def test_missing_file_returns_exit_code_2(tmp_path: Path) -> None:
    existing = tmp_path / "exists.env"
    existing.write_text("KEY=value\n")
    result = run([str(existing), str(tmp_path / "ghost.env")])
    assert result == 2


def test_json_output_is_valid_json(
    dev_env_file: Path, prod_env_file: Path, capsys: pytest.CaptureFixture
) -> None:
    run([str(dev_env_file), str(prod_env_file), "--format", "json"])
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert "missing" in parsed or "mismatches" in parsed or "status" in parsed


def test_mask_secrets_hides_values(
    dev_env_file: Path, prod_env_file: Path, capsys: pytest.CaptureFixture
) -> None:
    run([str(dev_env_file), str(prod_env_file), "--mask-secrets"])
    captured = capsys.readouterr()
    assert "dev-secret" not in captured.out
    assert "prod-secret" not in captured.out


def test_text_output_contains_key_names(
    dev_env_file: Path, prod_env_file: Path, capsys: pytest.CaptureFixture
) -> None:
    run([str(dev_env_file), str(prod_env_file)])
    captured = capsys.readouterr()
    assert "DEBUG" in captured.out
