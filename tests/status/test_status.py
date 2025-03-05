import pytest

def test_status(client) -> None:
   assert client.get("/status").status_code == 200
