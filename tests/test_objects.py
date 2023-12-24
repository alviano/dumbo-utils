from dumbo_utils.objects import Bunch


def test_bunch():
    bunch = Bunch(foo="bar")
    assert bunch.foo == "bar"
