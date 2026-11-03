import pytest

from config.settings import Settings

pytestmark = pytest.mark.unit


def test_captcha_wait_defaults_to_two_minutes(monkeypatch):
    monkeypatch.delenv("RM_CAPTCHA_WAIT", raising=False)

    assert Settings.from_env().captcha_wait == 120


def test_captcha_wait_can_be_overridden(monkeypatch):
    monkeypatch.setenv("RM_CAPTCHA_WAIT", "240")

    assert Settings.from_env().captcha_wait == 240
