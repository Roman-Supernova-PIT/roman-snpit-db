def test_version_is_string():
    from roman_snpit_db import __version__
    assert isinstance(__version__, str)
