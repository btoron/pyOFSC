import base64
import json
import logging
import urllib
from urllib.parse import urljoin

import requests

from .common import FULL_RESPONSE, JSON_RESPONSE, TEXT_RESPONSE, wrap_return
from .models import OFSApi, OFSConfig, OFSOAuthRequest


class OFSOauth2(OFSApi):
    @wrap_return(response_type=JSON_RESPONSE, expected=[200])
    def get_token(
        self, params: OFSOAuthRequest = OFSOAuthRequest()
    ) -> requests.Response:
        headers = self.headers
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        url = urljoin(self.baseUrl, "/rest/oauthTokenService/v2/token")
        response = requests.post(
            url, data=params.dict(exclude_none=True), headers=headers
        )
        return response
