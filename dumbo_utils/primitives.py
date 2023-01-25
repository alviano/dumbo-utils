import dataclasses
import functools
from dataclasses import InitVar
from typing import Optional, Union

import typeguard

from dumbo_utils import validation
from dumbo_utils.validation import validate, validate_does_not_have_attributes


def _arithmetic(cls):
    validate(cls.__name__, hasattr(cls, '__add__'), equals=False)
    validate(cls.__name__, hasattr(cls, '__mul__'), equals=False)
    validate(cls.__name__, hasattr(cls, '__rmul__'), equals=False)
    validate(cls.__name__, hasattr(cls, '__neg__'), equals=False)
    setattr(cls, '__add__', lambda self, other: cls(self.value + (other.value if type(other) == cls else other)))
    setattr(cls, '__mul__', lambda self, other: cls(self.value * (other.value if type(other) == cls else other)))
    setattr(cls, '__rmul__', lambda self, other: cls(self.value * (other.value if type(other) == cls else other)))
    setattr(cls, '__neg__', lambda self: getattr(cls, '__mul__')(-1))


@typeguard.typechecked
def bounded_integer(min_value: int, max_value: int):
    validate('min_value', min_value, max_value=max_value)

    def decorator(cls):
        validate_does_not_have_attributes(cls, [
            '__int__',
            'min_value',
            'max_value',
            'parse',
            'of',
            'toJSON',
        ], and_annotations=True)

        cls.__annotations__ = {'value': int}

        if getattr(cls, '__str__') == getattr(object, '__str__'):
            setattr(cls, '__str__', lambda self: str(self.value))

        setattr(cls, '__int__', lambda self: self.value)
        setattr(cls, 'min_value', staticmethod(lambda: min_value))
        setattr(cls, 'max_value', staticmethod(lambda: max_value))
        setattr(cls, 'parse', staticmethod(lambda s: cls(int(s))))
        setattr(cls, 'of', staticmethod(lambda s: cls(int(s))))

        if hasattr(cls, '__post_init__'):
            fun = getattr(cls, '__post_init__')

            def post_init(self):
                validate('value', self.value, min_value=self.min_value(), max_value=self.max_value())
                fun(self)
        else:
            def post_init(self):
                validate('value', self.value, min_value=self.min_value(), max_value=self.max_value())

        setattr(cls, '__post_init__', post_init)
        setattr(cls, 'toJSON', lambda self: self.value)
        setattr(cls, '__format__', lambda self, format_spec: self.value.__format__(format_spec))

        _arithmetic(cls)

        return dataclasses.dataclass(frozen=True, order=True)(cls)

    return decorator


@typeguard.typechecked
def bounded_string(min_length: int, max_length: int, pattern: str = r'.*'):
    validate('min_length', min_length, min_value=0, max_value=max_length)
    validate('max_length', max_length, min_value=min_length)

    def decorator(cls):
        validate_does_not_have_attributes(cls, [
            'min_length',
            'max_length',
            'pattern',
            'parse',
            'of',
            'toJSON',
            '__len__',
        ], and_annotations=True)

        cls.__annotations__ = {'value': str}

        if getattr(cls, '__str__') == getattr(object, '__str__'):
            setattr(cls, '__str__', lambda self: self.value)

        setattr(cls, 'min_length', staticmethod(lambda: min_length))
        setattr(cls, 'max_length', staticmethod(lambda: max_length))
        setattr(cls, 'pattern', staticmethod(lambda: pattern))
        setattr(cls, 'parse', staticmethod(lambda s: cls(s)))
        setattr(cls, 'of', staticmethod(lambda s: cls(s)))
        setattr(cls, 'toJSON', lambda self: self.value)
        setattr(cls, '__len__', lambda self: len(self.value))
        setattr(cls, 'length', property(lambda self: len(self.value)))

        if hasattr(cls, '__post_init__'):
            fun = getattr(cls, '__post_init__')

            def post_init(self):
                validate('value', self.value, min_len=self.min_length(), max_len=self.max_length(),
                         custom=validation.pattern(pattern))
                fun(self)
        else:
            def post_init(self):
                validate('value', self.value, min_len=self.min_length(), max_len=self.max_length(),
                         custom=validation.pattern(pattern))
        setattr(cls, '__post_init__', post_init)

        return dataclasses.dataclass(frozen=True, order=True)(cls)

    return decorator


@dataclasses.dataclass(frozen=True)
class PrivateKey:
    default_name: str = dataclasses.field(default="key")
    default_help_msg: str = dataclasses.field(default="Invalid call to private method")

    def validate(self, key: "PrivateKey", name: Optional[str] = None, help_msg: Optional[str] = None):
        validate(name if name is not None else self.default_name, key, equals=self,
                 help_msg=help_msg if help_msg is not None else self.default_help_msg)


@typeguard.typechecked
@functools.total_ordering
@dataclasses.dataclass(frozen=True)
class PositiveIntegerOrUnbounded:
    __value: Optional[int]

    key: InitVar[PrivateKey]
    __key = PrivateKey()

    def __post_init__(self, key: PrivateKey):
        self.__key.validate(key)

    @staticmethod
    def of(value: int) -> "PositiveIntegerOrUnbounded":
        validate("value", value, min_value=1)
        res = PositiveIntegerOrUnbounded(value, key=PositiveIntegerOrUnbounded.__key)
        return res

    @staticmethod
    def of_unbounded() -> "PositiveIntegerOrUnbounded":
        return PositiveIntegerOrUnbounded(None, key=PositiveIntegerOrUnbounded.__key)

    @property
    def int_value(self) -> int:
        validate("value", self.is_int, equals=True)
        return self.__value

    @property
    def is_int(self) -> bool:
        return self.__value is not None

    @property
    def is_unbounded(self) -> bool:
        return self.__value is None

    def __str__(self):
        return f"{self.__value}" if self.is_int else "unbounded"

    def __lt__(self, other: "PositiveIntegerOrUnbounded") -> bool:
        if self.is_unbounded:
            return False
        if other.is_unbounded:
            return True
        return self.__value < other.__value

    def greater_than(self, value: int) -> bool:
        return self.is_unbounded or self.__value > value

    def __add__(self, other: Union[int, "PositiveIntegerOrUnbounded"]) -> "PositiveIntegerOrUnbounded":
        if self.is_unbounded or (type(other) is PositiveIntegerOrUnbounded and other.is_unbounded):
            return PositiveIntegerOrUnbounded.of_unbounded()
        other_value = other.__value if type(other) is PositiveIntegerOrUnbounded else other
        return PositiveIntegerOrUnbounded.of(self.__value + other_value)
