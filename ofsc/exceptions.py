import logging


class OFSAPIException(Exception):
    def __init__(self, *args: object, **kwargs) -> None:
        super().__init__(*args)
        for key, value in kwargs.items():
            match key:
                case "status":
                    setattr(self, "status_code", int(value))
                case _:
                    setattr(self, key, value)
