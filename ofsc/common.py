import logging
from functools import wraps

TEXT_RESPONSE = 1
FULL_RESPONSE = 2
JSON_RESPONSE = 3


def wrap_return(*a, **kw):
    """
    Decorator @return_as wraps the function
    and decides the return type and if we launch an exception
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Pre:
            response_type = kwargs.get(
                "response_type", kw.get("response_type", FULL_RESPONSE)
            )
            kwargs.pop("response_type", None)
            response = func(*args, **kwargs)
            # post:
            logging.debug(response)

            if response_type == FULL_RESPONSE:
                return response
            elif response_type == JSON_RESPONSE:
                return response.json()
            else:
                return response.text
            return result

        return wrapper

    return decorator
