import logging

from django.views.generic.base import RedirectView, View
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.conf import settings
from django.contrib.auth import authenticate, login, REDIRECT_FIELD_NAME
from django.utils.http import url_has_allowed_host_and_scheme
from authbroker_client.utils import (
    get_client,
    AUTHORISATION_URL,
    TOKEN_URL,
    TOKEN_SESSION_KEY,
)

logger = logging.getLogger(__name__)

REDIRECT_SESSION_FIELD_NAME = f"_oauth2_{REDIRECT_FIELD_NAME}"
OAUTH_STATE_SESSION_KEY = TOKEN_SESSION_KEY + "_oauth_state"


def _request_fingerprint(request):
    """Fields that let us correlate the login leg with the callback leg and
    diagnose *why* the session state is missing. """
    return {
        "session_key": request.session.session_key,
        "cookie_present": settings.SESSION_COOKIE_NAME in request.COOKIES,
        "session_is_empty": request.session.is_empty(),
        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        "remote_addr": request.META.get("HTTP_X_FORWARDED_FOR")
        or request.META.get("REMOTE_ADDR", ""),
        "referer": request.META.get("HTTP_REFERER", ""),
    }


def get_next_url(request):
    next_url = request.GET.get(
        REDIRECT_FIELD_NAME,
        request.session.get(REDIRECT_SESSION_FIELD_NAME),
    )
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts=settings.ALLOWED_HOSTS, require_https=request.is_secure()
    ):
        return next_url
    if next_url:
        logger.info("next_url rejected by allow-list", extra={"next_url": next_url})
    return None


class AuthView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """Redirect to staff-sso"""
        auth_url_extra_kwargs = {}
        test_sso_token = getattr(
            settings, "TEST_SSO_PROVIDER_SET_RETURNED_ACCESS_TOKEN", None
        )
        if test_sso_token:
            auth_url_extra_kwargs["code"] = test_sso_token

        authorization_url, state = get_client(self.request).authorization_url(
            AUTHORISATION_URL, **auth_url_extra_kwargs
        )

        self.request.session[REDIRECT_SESSION_FIELD_NAME] = get_next_url(self.request)
        self.request.session[OAUTH_STATE_SESSION_KEY] = state

        # Force the session to persist now         
        was_new = self.request.session.session_key is None
        self.request.session.save()

        logger.info(
            "oauth login: state issued, redirecting to SSO",
            extra={
                "oauth_state": state,
                "session_was_new": was_new,
                **_request_fingerprint(self.request),
            },
        )
        return authorization_url


class AuthCallbackView(View):
    def get(self, request, *args, **kwargs):
        returned_state = request.GET.get("state")
        auth_code = request.GET.get("code", None)
        session_state = request.session.get(OAUTH_STATE_SESSION_KEY, None)

        meta = {
            "oauth_state_in_query": returned_state,
            "oauth_state_in_session": session_state,
            "code_present": bool(auth_code),
            **_request_fingerprint(request),
        }

        if not auth_code:
            logger.warning("oauth callback: missing auth code (400)", extra=meta)
            return HttpResponseBadRequest()

        if not session_state:
            logger.error("oauth callback: state missing from session (500)", extra=meta)
            return HttpResponseServerError()

        # NOTE: logging for now, but the request should fail is there's a state mismatch.
        if returned_state and returned_state != session_state:
            logger.error("oauth callback: query/session state mismatch", extra=meta)

        try:
            token = get_client(request).fetch_token(
                TOKEN_URL,
                client_secret=settings.AUTHBROKER_CLIENT_SECRET,
                code=auth_code,
            )
            request.session[TOKEN_SESSION_KEY] = dict(token)
            del request.session[OAUTH_STATE_SESSION_KEY]
            logger.info("oauth callback: token retrieved", extra=meta)
        except BaseException:
            logger.exception("oauth callback: failed to retrieve access token", extra=meta)

        user = authenticate(request)
        if user is not None:
            login(request, user)
        else:
            logger.warning("oauth callback: authenticate() returned no user", extra=meta)

        next_url = get_next_url(request) or getattr(settings, "LOGIN_REDIRECT_URL", "/")
        return redirect(next_url)
