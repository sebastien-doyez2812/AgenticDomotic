from ambiance import set_music


def test_set_music_default(capsys):
    result = set_music(style="rock", volume=50)
    assert result is True

    