from ambiance import set_musique


def test_set_musique_default(capsys):
    result = set_musique()
    assert result is True

    