import dataclasses
from dataclasses import InitVar
from typing import Any, Final

import pytest

from dumbo_utils.primitives import PrivateKey, bounded_string, bounded_integer, PositiveIntegerOrUnbounded
from dumbo_utils.validation import validate


@pytest.mark.parametrize("min_value", list(range(10)))
def test_bounded_integer_min_value(min_value):
    @bounded_integer(min_value=min_value, max_value=min_value + 10)
    class Foo:
        ...

    assert Foo(min_value).value == Foo.min_value()
    with pytest.raises(ValueError):
        Foo(min_value - 1)


@pytest.mark.parametrize("max_value", list(range(10)))
def test_bounded_integer_max_value(max_value):
    @bounded_integer(min_value=0, max_value=max_value)
    class Foo:
        ...

    assert Foo(max_value).value == Foo.max_value()
    with pytest.raises(ValueError):
        Foo(max_value + 1)


def test_bounded_integer_with_post_init():
    @bounded_integer(min_value=10, max_value=20)
    class Even:
        def __post_init__(self):
            validate("value", self.value, custom=lambda value: value % 2 == 0)

    assert Even(10).value == 10

    with pytest.raises(ValueError):
        Even(11)


@pytest.mark.parametrize("min_length", list(range(10)))
def test_bounded_string_min_length(min_length):
    @bounded_string(min_length=min_length, max_length=min_length + 10)
    class Foo:
        ...

    # assert len(Foo("A" * min_length)) == Foo.min_length()
    assert Foo("A" * min_length).length == Foo.min_length()
    if min_length > 0:
        with pytest.raises(ValueError):
            Foo("A" * (min_length - 1))


@pytest.mark.parametrize("max_length", list(range(10)))
def test_bounded_string_max_length(max_length):
    @bounded_string(min_length=0, max_length=max_length)
    class Foo:
        ...

    assert Foo("A" * max_length).length == Foo.max_length()
    with pytest.raises(ValueError):
        Foo("A" * (max_length + 1))


def test_bounded_string_pattern():
    @bounded_string(min_length=0, max_length=10, pattern=r"[A-Z]*")
    class Foo:
        ...

    assert Foo("A" * 5).length == 5
    with pytest.raises(ValueError):
        Foo("a" * 5)


def test_bounded_string_with_post_init():
    @bounded_string(min_length=2, max_length=2)
    class Foo:
        def __post_init__(self):
            validate("value", self.value[0] != self.value[1], equals=True)

    assert Foo("AB").value == "AB"
    with pytest.raises(ValueError):
        Foo("AA")


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


def test_positive_integer_or_unbounded():
    assert PositiveIntegerOrUnbounded.of(1).int_value == 1
    assert PositiveIntegerOrUnbounded.of_unbounded().is_unbounded
    with pytest.raises(ValueError):
        _ = PositiveIntegerOrUnbounded.of_unbounded().int_value
    with pytest.raises(ValueError):
        PositiveIntegerOrUnbounded.of(0)


def test_positive_integer_or_unbounded_order():
    assert PositiveIntegerOrUnbounded.of(1) < PositiveIntegerOrUnbounded.of(2)
    assert PositiveIntegerOrUnbounded.of(1) < PositiveIntegerOrUnbounded.of_unbounded()


def test_positive_integer_or_unbounded_addition():
    assert PositiveIntegerOrUnbounded.of(1) + PositiveIntegerOrUnbounded.of(1) == PositiveIntegerOrUnbounded.of(2)
    assert PositiveIntegerOrUnbounded.of(1) + PositiveIntegerOrUnbounded.of_unbounded() == \
           PositiveIntegerOrUnbounded.of_unbounded()
    assert PositiveIntegerOrUnbounded.of(1) + 0 == PositiveIntegerOrUnbounded.of(1)
    with pytest.raises(ValueError):
        PositiveIntegerOrUnbounded.of(1) + (-1)
