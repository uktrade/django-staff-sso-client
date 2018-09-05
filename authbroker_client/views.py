from django.views.generic.base import RedirectView, View
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.conf import settings

from raven.contrib.django.raven_compat.models import client
from .client import get_client, AUTHORISATION_URL, TOKEN_URL, TOKEN_SESSION_KEY


class AuthView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):

        authorization_url, state = get_client(self.request).authorization_url(AUTHORISATION_URL)

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

            profile = get_client(self.request)

            self.request.session[TOKEN_SESSION_KEY] = dict(token)

            del self.request.session[TOKEN_SESSION_KEY + '_oauth_state']

        # NOTE: the BaseException will be removed or narrowed at a later date. The try/except block is
        # here due to reports of the app raising a 500 if the url is copied.  Current theory is that
        # somehow the url with the authcode is being copied, which would cause `fetch_token` to raise
        # an exception. However, looking at the fetch_code method, I'm not entirely sure what exceptions it
        # would raise in this instance.
        except BaseException:
            client.captureException()
            return redirect('authbroker_login')

        # TODO: make the redirect url configurable
        return redirect('/')
