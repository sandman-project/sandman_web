"""Tests initialization."""

import sandman_web


def test_config() -> None:
    """Test app configuration."""
    assert not sandman_web.create_app().testing
    assert sandman_web.create_app({"TESTING": True}).testing
