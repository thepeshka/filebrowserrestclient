from typing import Type, Callable, List, TypeVar


M = TypeVar("M")


def response_model(_type: Type[M]) -> Callable[[Callable[..., dict]], Callable[..., M]]:
    def inner(f: Callable[..., dict]) -> Callable[..., M]:
        def wrapped(*args, **kwargs):
            return _type.parse_obj(f(*args, **kwargs))
        return wrapped
    return inner


def response_list_model(_type: Type[M]) -> Callable[[Callable[..., List[dict]]], Callable[..., List[M]]]:
    def inner(f: Callable[..., List[dict]]) -> Callable[..., List[M]]:
        def wrapped(*args, **kwargs):
            return [_type.parse_obj(o) for o in f(*args, **kwargs)]
        return wrapped
    return inner
