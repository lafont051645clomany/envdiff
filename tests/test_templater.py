"""Tests for envdiff.templater."""

import pytest

from envdiff.templater import (
    EnvTemplate,
    TemplateEntry,
    build_template,
    generate_example,
    render_template,
)


@pytest.fixture
def simple_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "s3cr3t",
        "PORT": "8080",
        "API_SECRET_KEY": "abc123",
    }


def test_build_template_returns_all_keys(simple_env):
    template = build_template(simple_env)
    keys = {e.key for e in template.entries}
    assert keys == set(simple_env.keys())


def test_build_template_values_are_placeholders(simple_env):
    template = build_template(simple_env)
    for entry in template.entries:
        assert entry.placeholder != simple_env[entry.key]


def test_secret_keys_get_secret_placeholder(simple_env):
    template = build_template(simple_env)
    secrets = {e.key: e for e in template.entries if e.is_secret}
    assert "DB_PASSWORD" in secrets
    assert "API_SECRET_KEY" in secrets
    for entry in secrets.values():
        assert entry.placeholder == "<secret>"


def test_non_secret_placeholder_uses_key_name(simple_env):
    template = build_template(simple_env)
    port_entry = next(e for e in template.entries if e.key == "PORT")
    assert port_entry.placeholder == "<port>"
    assert not port_entry.is_secret


def test_include_comments_adds_secret_comment(simple_env):
    template = build_template(simple_env, include_comments=True)
    secret_entries = [e for e in template.entries if e.is_secret]
    for entry in secret_entries:
        assert entry.comment == "# secret"


def test_exclude_comments_no_comment(simple_env):
    template = build_template(simple_env, include_comments=False)
    for entry in template.entries:
        assert entry.comment is None


def test_render_template_contains_all_keys(simple_env):
    template = build_template(simple_env)
    rendered = render_template(template)
    for key in simple_env:
        assert key in rendered


def test_render_template_no_original_values(simple_env):
    template = build_template(simple_env)
    rendered = render_template(template)
    for value in simple_env.values():
        assert value not in rendered


def test_render_template_ends_with_newline(simple_env):
    template = build_template(simple_env)
    rendered = render_template(template)
    assert rendered.endswith("\n")


def test_render_empty_template():
    template = EnvTemplate(entries=[])
    rendered = render_template(template)
    assert rendered == ""


def test_generate_example_convenience(simple_env):
    output = generate_example(simple_env)
    assert "DB_PASSWORD=<secret>" in output
    assert "PORT=<port>" in output


def test_to_dict(simple_env):
    template = build_template(simple_env)
    d = template.to_dict()
    assert set(d.keys()) == set(simple_env.keys())
    assert d["DB_PASSWORD"] == "<secret>"
