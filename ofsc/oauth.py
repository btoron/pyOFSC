import requests

from .common import OBJ_RESPONSE, wrap_return
from .models import OFSApi, OFSOAuthRequest


class OFSOauth2(OFSApi):
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_token(
        self, params: OFSOAuthRequest = OFSOAuthRequest()
    ) -> requests.Response:
        return self.token(auth=params)
