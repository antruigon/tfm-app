from utils import clean_mention


def test_clean_mention():
    assert clean_mention("<@U123> hola equipo") == "hola equipo"
