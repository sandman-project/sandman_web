import pytest

import sandman_web

def test_config() -> None:
   assert not sandman_web.create_app().testing
   assert sandman_web.create_app({"TESTING": True}).testing