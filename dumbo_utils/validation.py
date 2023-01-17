import re
from typing import Callable

import typeguard
import valid8

validate = valid8.validate
ValidationError = valid8.ValidationError


@typeguard.typechecked
def pattern(regex: str) -> Callable[[str], bool]:
    r = re.compile(regex)

    def res(value):
        return bool(r.fullmatch(value))

    res.__name__ = f'pattern({regex})'
    return res
