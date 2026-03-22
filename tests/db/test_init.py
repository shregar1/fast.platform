"""Basic tests for db."""

def test_import():
    import db
    assert db.__version__ == "0.1.0"
