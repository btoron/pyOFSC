import logging
from functools import wraps

import pydantic

from .exceptions import OFSAPIException

TEXT_RESPONSE = 1
FULL_RESPONSE = 2
OBJ_RESPONSE = 3
FILE_RESPONSE = 4


def wrap_return(*decorator_args, **decorator_kwargs):
    """
    Decorator @wrap_return wraps the function
    and decides the return type and if we launch an exception
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*func_args, **func_kwargs):
            logging.debug(
                f"{func_args=}, {func_kwargs=}, {decorator_args=}, {decorator_kwargs=}"
            )
            config = func_args[0].config
            # Pre:
            response_type = func_kwargs.get(
                "response_type", decorator_kwargs.get("response_type", OBJ_RESPONSE)
            )
            func_kwargs.pop("response_type", None)
            expected_codes = decorator_kwargs.get("expected", [200])
            model: pydantic.BaseModel | None = func_kwargs.get(
                "model", decorator_kwargs.get("model", None)
            )
            func_kwargs.pop("model", None)

            response = func(*func_args, **func_kwargs)
            # post:
            logging.debug(response)

            if response_type == FULL_RESPONSE:
                return response
            elif response_type == OBJ_RESPONSE:
                logging.debug(
                    f"{response_type=}, {config.auto_model=}, {model=} {func_args= } {func_kwargs=}"
                )
                if response.status_code in expected_codes:
                    match response.status_code:
                        case 204:
                            return response.text
                        case _:
                            data_response = response.json()
                            if config.auto_model and model is not None:
                                # Remove the links unless there is a field called links in the model
                                if not hasattr(model, "links"):
                                    del data_response["links"]
                                return model.model_validate(data_response)
                            else:
                                return data_response
                else:
                    if not config.auto_raise:
                        return response.json()
                    # Check if response.statyus code is between 400 and 499
                    if 400 <= response.status_code < 500:
                        logging.error(response.json())
                        raise OFSAPIException(**response.json())
                    elif 500 <= response.status_code < 600:
                        raise OFSAPIException(**response.json())
            elif response_type == FILE_RESPONSE:
                if response.status_code in expected_codes:
                    # We return the filed content in a bytes object
                    return response.content
                else:
                    if not config.auto_raise:
                        return response.json()
                    # Check if response.statyus code is between 400 and 499
                    if 400 <= response.status_code < 500:
                        logging.error(response.json())
                        raise OFSAPIException(**response.json())
                    elif 500 <= response.status_code < 600:
                        raise OFSAPIException(**response.json())
            else:
                return response.text

        return wrapper

    return decorator
