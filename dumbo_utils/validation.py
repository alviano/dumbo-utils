import re
from typing import Callable

import typeguard
import valid8

validate = valid8.validate
ValidationError = valid8.ValidationError


@typeguard.typechecked
def pattern(regex: str) -> Callable[[str], bool]:
    if regex == '.*':
        return lambda value: True

    r = re.compile(regex)

    def res(value):
        return bool(r.fullmatch(value))

    res.__name__ = f'pattern({regex})'
    return res


@typeguard.typechecked
def validate_does_not_have_attributes(cls, attributes: list[str], and_annotations: bool = False):
    if and_annotations:
        validate(
            f"{cls.__name__} has no attribute __annotations__",
            hasattr(cls, '__annotations__') and cls.__annotations__ != {},
            equals=False
        )
    for attribute in attributes:
        validate(f"{cls.__name__} has no attribute {attribute}", hasattr(cls, attribute), equals=False)
