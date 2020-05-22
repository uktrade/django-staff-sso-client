from django.views.generic.base import RedirectView, View
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.conf import settings
from django.contrib.auth import authenticate, login

from authbroker_client.utils import get_client, AUTHORISATION_URL, TOKEN_URL, \
    TOKEN_SESSION_KEY
try:
    from raven.contrib.django.raven_compat.models import client
    capture_exception = client.captureException
except ImportError:
    from sentry_sdk import capture_exception


class AuthView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):

        auth_url_extra_kwargs = {}

        # Allow for compatibility with https://github.com/uktrade/mock-sso
        # during testing. See tests/settings.py for details.
        test_sso_token = getattr(
            settings,
            'TEST_SSO_PROVIDER_SET_RETURNED_ACCESS_TOKEN',
            None,
        )
        if test_sso_token:
            auth_url_extra_kwargs['code'] = test_sso_token

        authorization_url, state = get_client(self.request).authorization_url(
            AUTHORISATION_URL,
            **auth_url_extra_kwargs,
        )

        self.request.session[TOKEN_SESSION_KEY + '_oauth_state'] = state

        return authorization_url


class AuthCallbackView(View):
    def get(self, request, *args, **kwargs):

        auth_code = request.GET.get('code', None)

        if not auth_code:
            return HttpResponseBadRequest()

        state = self.request.session.get(TOKEN_SESSION_KEY + '_oauth_state', None)

        if not state:
            return HttpResponseServerError()

        try:
            token = get_client(self.request).fetch_token(
                TOKEN_URL,
                client_secret=settings.AUTHBROKER_CLIENT_SECRET,
                code=auth_code)

            self.request.session[TOKEN_SESSION_KEY] = dict(token)

            del self.request.session[TOKEN_SESSION_KEY + '_oauth_state']

        # NOTE: the BaseException will be removed or narrowed at a later date. The try/except block is
        # here due to reports of the app raising a 500 if the url is copied.  Current theory is that
        # somehow the url with the authcode is being copied, which would cause `fetch_token` to raise
        # an exception. However, looking at the fetch_code method, I'm not entirely sure what exceptions it
        # would raise in this instance.
        except BaseException:
            capture_exception()

        # create the user
        user = authenticate(request)

        if user is not None:
            login(request, user)

        return redirect(getattr(settings, 'LOGIN_REDIRECT_URL', '/'))
