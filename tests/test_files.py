from dumbo_utils import files


def test_load_file():
    assert files.load_file(__file__, "../LICENSE") == open("../LICENSE").read()
