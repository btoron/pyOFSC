import logging

from .common import FULL_RESPONSE, OBJ_RESPONSE, TEXT_RESPONSE
from .core import OFSCore
from .metadata import OFSMetadata
from .models import OFSConfig
from .oauth import OFSOauth2


class OFSC:

    # the default URL becomes {companyname}.fs.ocs.oraclecloud.com
    def __init__(
        self,
        clientID,
        companyName,
        secret,
        root=None,
        baseUrl=None,
        useToken=False,
        enable_auto_raise=True,
        enable_auto_model=True,
    ):

        self._config = OFSConfig(
            baseURL=baseUrl,
            clientID=clientID,
            secret=secret,
            companyName=companyName,
            root=root,
            useToken=useToken,
            auto_raise=enable_auto_raise,  # 20240401: This is a new feature that will raise an exception if the API returns an error
            auto_model=enable_auto_model,  # 20240401: This is a new feature that will return a pydantic model if the API returns a 200
        )
        self._core = OFSCore(config=self._config)
        self._metadata = OFSMetadata(config=self._config)
        self._oauth = OFSOauth2(config=self._config)

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
    def core(self) -> OFSCore:
        if not self._core:
            self._core = OFSCore(config=self._config)
        return self._core

    @property
    def metadata(self) -> OFSMetadata:
        if not self._metadata:
            self._metadata = OFSMetadata(config=self._config)
        return self._metadata

    @property
    def oauth2(self) -> OFSOauth2:
        if not self._oauth:
            self._oauth = OFSOauth2(config=self._config)
        return self._oauth

    @property
    def auto_model(self):
        return self._config.auto_model

    @auto_model.setter
    def auto_model(self, value):
        self._config.auto_model = value
        self._core.config.auto_model = value
        self._metadata.config.auto_model = value
        self._oauth.config.auto_model = value

    def __str__(self) -> str:
        return f"baseURL={self._config.baseURL}"

    def __getattr__(self, method_name):
        """Function to wrap calls to methods directly withoud invoking the right API

        Args:
            method_name (_type_): Unknown method to call

        """

        def wrapper(*args, **kwargs):
            if method_name in self._core_methods:
                raise NotImplementedError(
                    f"{method_name} was called without the API name (Core). This was deprecated in OFSC 2.0"
                )

            if method_name in self._metadata_methods:
                raise NotImplementedError(
                    f"{method_name} was called without the API name (Metadata). This was deprecated in OFSC 2.0"
                )
            raise Exception("method not found")

        return wrapper
