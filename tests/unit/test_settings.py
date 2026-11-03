import pytest

from config.settings import Settings

pytestmark = pytest.mark.unit


def test_captcha_wait_defaults_to_two_minutes(monkeypatch):
    monkeypatch.delenv("RM_CAPTCHA_WAIT", raising=False)

    assert Settings.from_env().captcha_wait == 120


def test_captcha_wait_can_be_overridden(monkeypatch):
    monkeypatch.setenv("RM_CAPTCHA_WAIT", "240")

    assert Settings.from_env().captcha_wait == 240


def test_headless_mode_is_enabled_by_default(monkeypatch):
    monkeypatch.delenv("RM_HEADLESS", raising=False)

    assert Settings.from_env().headless is True


def test_headless_mode_can_be_disabled(monkeypatch):
    monkeypatch.setenv("RM_HEADLESS", "false")

    assert Settings.from_env().headless is False
