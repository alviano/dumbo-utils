from dumbo_utils.url import compress_object_for_url


def test_compress_object_for_url():
    assert compress_object_for_url({"foo": "bar"}) == "eJxLrfTKTTKyyPTP9MqMjPDMTAu0tQUASdgGyg==%21"


def test_compress_object_for_url_append_bang():
    assert compress_object_for_url({"foo": "bar"}) == "eJxLrfTKTTKyyPTP9MqMjPDMTAu0tQUASdgGyg==%21"
