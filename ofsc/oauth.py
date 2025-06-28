# TODO: Phase 1.6 - Migrate from requests to httpx
import mockup_requests as requests
from urllib.parse import urljoin

from .common import OBJ_RESPONSE, wrap_return
from .models import OFSApi, OFSOAuthRequest


class OFSOauth2(OFSApi):
    @wrap_return(response_type=OBJ_RESPONSE, expected=[200])
    def get_token(
        self, params: OFSOAuthRequest = OFSOAuthRequest()
    ) -> requests.Response:
        return self.token(auth=params)
    
    def token(self, auth: OFSOAuthRequest) -> requests.Response:
        """Request OAuth2 token from OFSC API.
        
        Args:
            auth: OAuth2 authentication request parameters
            
        Returns:
            Response containing the OAuth2 token
        """
        url = urljoin(self.baseUrl, "/rest/ofscOAuth/v1/token")
        
        # Prepare request data
        data = {
            "grant_type": auth.grant_type
        }
        if auth.assertion:
            data["assertion"] = auth.assertion
            
        return requests.post(url, headers=self.headers, data=data)
