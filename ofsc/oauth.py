"""OAuth2 Authentication module for OFSC Python Wrapper.

This module provides backward compatibility for the legacy OAuth2 implementation
while internally using the modern authentication system from auth.py.

All OAuth logic has been consolidated in auth.py - this module now serves
as a compatibility wrapper to maintain existing API contracts.
"""

from typing import TYPE_CHECKING

from .auth import OAuth2Auth
from .exceptions import OFSAuthenticationException
from .models import OFSApi, OFSOAuthRequest

if TYPE_CHECKING:
    from .auth import OAuth2TokenResponse


class OFSOauth2(OFSApi):
    """OAuth2 client for OFSC API (legacy compatibility wrapper).
    
    This class maintains backward compatibility with existing code while
    internally using the modern OAuth2Auth implementation from auth.py.
    
    The simplified interface provides a single get_token() method that
    returns OAuth2TokenResponse objects directly.
    """
    
    def get_token(self, params: OFSOAuthRequest = None) -> 'OAuth2TokenResponse':
        """Get OAuth2 token using modern authentication system.
        
        Args:
            params: OAuth2 authentication request parameters (for compatibility,
                   actual token request uses client_credentials grant type)
            
        Returns:
            OAuth2TokenResponse containing access_token, token_type, expires_in, etc.
            
        Raises:
            OFSAuthenticationException: If token request fails or OAuth2 not configured
        """
        # Get OAuth2Auth instance from OFSConfig
        oauth2_auth = self._config._get_auth_instance()
        
        if not isinstance(oauth2_auth, OAuth2Auth):
            raise OFSAuthenticationException(
                "OAuth2 authentication not enabled. Set useToken=True in configuration."
            )
        
        # Use the simplified get_token interface from OAuth2Auth
        return oauth2_auth.get_token()
