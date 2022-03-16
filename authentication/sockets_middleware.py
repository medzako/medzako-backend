# Third party imports
from urllib.parse import urlparse, parse_qs
from channels.auth import AuthMiddlewareStack
# DRF imports.
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
# Django imports.
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from channels.middleware import BaseMiddleware

from core.utils.consumer_database_helpers import get_user




class TokenAuthMiddleware(BaseMiddleware):
    """
    Token authorization middleware for channels
    """
    def __init__(self, inner):
            super().__init__(inner)

    async def __call__(self, scope, receive, send):
        try:
            token_key = (dict((x.split('=') for x in scope['query_string'].decode().split("&")))).get('token', None)
        except ValueError:
            token_key = None
        scope['user'] = AnonymousUser() if token_key is None else await get_user(token_key)
        return await super().__call__(scope, receive, send)
