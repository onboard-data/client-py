from .exceptions import OnboardApiException, OnboardTemporaryException
from typing import List, Iterable, TypeVar

T = TypeVar('T')


def divide_chunks(input_list: List[T], n: int) -> Iterable[List[T]]:
    # looping till length input_list
    for i in range(0, len(input_list), n):
        yield input_list[i:i + n]


def json(func):
    """Decorator for making sure requests responses are handled consistently"""
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
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
