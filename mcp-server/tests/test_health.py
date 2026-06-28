from app import echo, ping


def test_echo():
    assert echo("hola") == "Echo desde MCP: hola"


def test_ping():
    assert ping() == "pong"
