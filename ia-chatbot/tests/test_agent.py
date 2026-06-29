from agent import _extract_echo_message, _wants_echo, _wants_ping


def test_wants_ping():
    assert _wants_ping("haz ping al mcp")
    assert _wants_ping("comprueba mcp por favor")
    assert not _wants_ping("hola, qué es kubernetes?")


def test_wants_echo():
    assert _wants_echo("echo hola mundo")
    assert _wants_echo("repite esto")
    assert not _wants_echo("solo una pregunta")


def test_extract_echo_message():
    assert _extract_echo_message("echo hola") == "hola"
    assert _extract_echo_message("repite: prueba") == "prueba"
    assert _extract_echo_message("ECHO: test") == "test"
