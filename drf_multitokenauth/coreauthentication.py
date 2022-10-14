"""
Provides our custom MultiToken Authentication (based on normal Token Authentication)
"""
from rest_framework.authentication import TokenAuthentication

from drf_multitokenauth.models import MultiToken

# try to import memoize
memoize = None

try:
    from memoize import memoize
except ImportError:
    pass


class MultiTokenAuthentication(TokenAuthentication):
    """
    Simple token based authentication.

    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:

        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    # override get_model (use a custom model)
    def get_model(self):
        if self.model is not None:
            return self.model
        return MultiToken


# if memoize is available, create a cached multi token authentication class, which uses redis as a cache
if memoize:
    class CachedMultiTokenAuthentication(MultiTokenAuthentication):
        """
        Cached MultiTokenAuthentication, using django-memoize
        """
        @memoize(timeout=60)
        def authenticate_credentials(self, key):
            return super(CachedMultiTokenAuthentication, self).authenticate_credentials(key)

        def __repr__(self):
            return self.__class__.__name__
