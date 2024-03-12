import logging
from functools import wraps

import requests

from .exceptions import OFSAPIException

TEXT_RESPONSE = 1
FULL_RESPONSE = 2
JSON_RESPONSE = 3


def wrap_return(*a, **kw):
    """
    Decorator @wrap_return wraps the function
    and decides the return type and if we launch an exception
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = args[0].config
            # Pre:
            response_type = kwargs.get(
                "response_type", kw.get("response_type", FULL_RESPONSE)
            )
            expected_codes = kw.get("expected_codes", [200])
            kwargs.pop("response_type", None)
            response = func(*args, **kwargs)
            # post:
            logging.debug(response)

            if response_type == FULL_RESPONSE:
                return response
            elif response_type == JSON_RESPONSE:
                if response.status_code in expected_codes:
                    return response.json()
                else:
                    if not config.auto_raise:
                        return response.json()
                    # Check if response.statyus code is between 400 and 499
                    if 400 <= response.status_code < 500:
                        raise OFSAPIException(**response.json())
                    elif 500 <= response.status_code < 600:
                        raise OFSAPIException(**response.json())
            else:
                return response.text

        return wrapper

    return decorator
