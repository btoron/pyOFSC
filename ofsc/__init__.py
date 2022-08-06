import base64
import logging
from http import client
from urllib import response
from warnings import warn

from .common import FULL_RESPONSE, JSON_RESPONSE, TEXT_RESPONSE
from .core import OFSCore
from .metadata import OFSMetadata
from .models import OFSConfig


class OFSC:

    API_PORTAL = "https://api.etadirect.com"

    def __init__(self, clientID, companyName, secret, baseUrl=API_PORTAL):
        self._config = OFSConfig(
            baseURL=baseUrl, clientID=clientID, secret=secret, companyName=companyName
        )
        self.headers = {}
        self.headers["Authorization"] = "Basic " + self._config.authString.decode(
            "utf-8"
        )
        self._core = OFSCore(config=self._config)
        self._metadata = OFSMetadata(config=self._config)

        # For compatibility we build dynamically the method list of the submodules
        self._core_methods = [
            attribute
            for attribute in dir(OFSCore)
            if callable(getattr(OFSCore, attribute))
            and attribute.startswith("_") is False
        ]
        self._metadata_methods = [
            attribute
            for attribute in dir(OFSMetadata)
            if callable(getattr(OFSMetadata, attribute))
            and attribute.startswith("_") is False
        ]

    @property
    def core(self):
        if not self._core:
            self._core = OFSCore(config=self._config)
        return self._core

    @property
    def metadata(self):
        if not self._metadata:
            self._metadata = OFSMetadata(config=self._config)
        return self._metadata

    def __getattr__(self, method_name):
        """Function to wrap calls to methods directly withoud invoking the right API

        Args:
            method_name (_type_): Unknown method to call

        """

        def wrapper(*args, **kwargs):
            if method_name in self._core_methods:
                warn(
                    f"{method_name} was called without the API name (Core). This will be deprecated in OFSC 2.0",
                    DeprecationWarning,
                )
                return getattr(self.core, method_name)(*args, **kwargs)

            if method_name in self._metadata_methods:
                warn(
                    f"{method_name} was called without the API name (Metadata). This will be deprecated in OFSC 2.0",
                    DeprecationWarning,
                )
                return getattr(self.metadata, method_name)(*args, **kwargs)
            raise Exception("method not found")

        return wrapper
