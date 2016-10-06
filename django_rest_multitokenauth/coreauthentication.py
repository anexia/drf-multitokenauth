"""
Provides our custom MultiToken Authentication (based on normal Token Authentication)
"""
from __future__ import unicode_literals

from rest_framework.authentication import TokenAuthentication

from eric.coreauth.models import MultiToken


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
