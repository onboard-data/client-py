import requests
from .exceptions import OnboardApiException, OnboardTemporaryException
from typing import List, Iterable, TypeVar, Callable

T = TypeVar('T')


def divide_chunks(input_list: List[T], n: int) -> Iterable[List[T]]:
    # looping till length input_list
    for i in range(0, len(input_list), n):
        yield input_list[i:i + n]


def json(func: Callable[..., T]) -> Callable[..., T]:
    """Decorator for making sure requests responses are handled consistently"""
    # the type annotations on json are a lie to let us type the methods in client
    # with approximate descriptions of the JSON they return, even though the methods
    # as implemented return requests.Response objects
    def wrapper(*args, **kwargs):
        try:
            res: requests.Response = func(*args, **kwargs)  # type: ignore[assignment]
            if res is None:
                return None

            # remove the cached access token if authorization failed
            # it's likely just expired
            if res.status_code == 401 and args[0].token is not None:
                args[0].token = None
                return wrapper(*args, **kwargs)

            if res.status_code > 499:
                raise OnboardTemporaryException(res.text or res.status_code)
            if res.status_code > 399:
                raise OnboardApiException(res.text or res.status_code)

            if hasattr(wrapper, 'raw_response'):
                return res
            return res.json()
        except OnboardApiException as e:
            raise e
        except Exception as e:
            raise OnboardApiException(e)
    return wrapper
