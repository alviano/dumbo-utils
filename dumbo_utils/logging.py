from typing import Iterable

import logging


def log(level, func):
    if level >= logging.root.level:
        data = func()
        args, kwargs = (), {}
        if type(data) is str:
            msg = data
        else:
            assert isinstance(data, Iterable)
            data = list(data)
            if len(data) == 2:
                msg, args = data
            else:
                assert len(data) == 3
                msg, args, kwargs = data
        assert type(data) is str
        assert isinstance(args, Iterable)
        assert isinstance(kwargs, dict)
        logging.log(level, msg, *args, **kwargs)


def dlog(level, func):
    if __debug__:
        log(level, func)

