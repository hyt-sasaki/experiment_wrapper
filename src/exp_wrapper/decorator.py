# -*- coding:utf-8 -*-
import functools


def arg_decorator(name):
    def _arg_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, 'parents_dict'):
                self.parents_dict = {}
            parser = func(self, *args, **kwargs)
            self.parents_dict[name] = parser
        return wrapper
    return _arg_decorator
