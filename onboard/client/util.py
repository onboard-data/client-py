from .exceptions import OnboardApiException, OnboardTemporaryException


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


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
                raise OnboardTemporaryException(res.text)
            if res.status_code > 399:
                raise OnboardApiException(res.text)

            if hasattr(wrapper, 'raw_response'):
                return res
            return res.json()
        except OnboardApiException as e:
            raise e
        except Exception as e:
            raise OnboardApiException(e)
    return wrapper
