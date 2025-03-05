import functools
from urllib.parse import urljoin, urlparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect
from django.urls import reverse

from requests_oauthlib import OAuth2Session


TOKEN_SESSION_KEY = '_authbroker_token'

AUTHORISATION_URL = urljoin(settings.AUTHBROKER_URL, '/o/authorize/')

AUTHBROKER_URL = getattr(settings, 'AUTHBROKER_INTERNAL_URL', settings.AUTHBROKER_URL)
PROFILE_URL = urljoin(AUTHBROKER_URL, '/api/v1/user/me/')
INTROSPECT_URL = urljoin(AUTHBROKER_URL, 'o/introspect/')
TOKEN_URL = urljoin(AUTHBROKER_URL, '/o/token/')

TOKEN_CHECK_PERIOD_SECONDS = 60


def check_config():
    """
    Sanity check settings.
    """
    if not urlparse(AUTHORISATION_URL).scheme:
        # Not having a protocol means when urljoin is used later in the code the first part of the URL is discarded
        # leading to the suprising effect that auth urls redirect to localhost not the remote SSO.
        raise ImproperlyConfigured("AUTHBROKER_URL must start with protocol, e.g. https://")


def get_client(request, **kwargs):
    callback_url = reverse('authbroker_client:callback')
    redirect_uri = request.build_absolute_uri(callback_url)

    return OAuth2Session(
        settings.AUTHBROKER_CLIENT_ID,
        redirect_uri=redirect_uri,
        scope=get_scope(),
        token=request.session.get(TOKEN_SESSION_KEY, None),
        **kwargs)


def get_scope():
    return getattr(settings, 'AUTHBROKER_STAFF_SSO_SCOPE', 'read write')


def has_valid_token(client):
    """Does the session have a valid token?"""

    return client.authorized


def get_profile(client):
    return client.get(PROFILE_URL).json()


def authbroker_login_required(func):
    """Check that the current session has authenticated with the authbroker and has a valid token.
    This is different to the @login_required decorator in that it only checks for a valid authbroker Oauth2 token,
    not an authenticated django user."""

    @functools.wraps(func)
    def decorated(request):
        if not has_valid_token(get_client(request)):
            return redirect('authbroker:login')

        return func(request)
    return decorated


check_config()
