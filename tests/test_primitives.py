import dataclasses
from dataclasses import InitVar
from typing import Any, Final

import pytest

from dumbo_utils.primitives import PrivateKey


def test_private_key():
    @dataclasses.dataclass
    class Foo:
        key: InitVar[Any]
        __key: Final = PrivateKey()

        def __post_init__(self, key: Any):
            self.__key.validate(key)

        @staticmethod
        def of():
            return Foo(Foo.__key)

    Foo.of()
    with pytest.raises(ValueError):
        Foo(object())
