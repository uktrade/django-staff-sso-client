import logging

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.cache import caches

from authbroker_client.utils import TOKEN_SESSION_KEY

logger = logging.getLogger(__name__)

OAUTH_STATE_SESSION_KEY = TOKEN_SESSION_KEY + "_oauth_state"
REDIRECT_SESSION_FIELD_NAME = f"_oauth2_{REDIRECT_FIELD_NAME}"

CACHE_STATE_KEY_PREFIX = "_authbroker_oauth_state"
DEFAULT_STATE_TTL_SECONDS = 600


def use_cache_state_store():
    return getattr(settings, "AUTHBROKER_USE_CACHE_STATE_STORE", False)


def _cache():
    alias = getattr(settings, "AUTHBROKER_STATE_CACHE_ALIAS", "default")
    return caches[alias]


def _cache_key(state):
    return f"{CACHE_STATE_KEY_PREFIX}_{state}"


def _state_ttl():
    return getattr(
        settings, "AUTHBROKER_STATE_TTL_SECONDS", DEFAULT_STATE_TTL_SECONDS
    )


def store_state(request, state, next_url):
    """Persist the `state` value along with the redirect url."""
    if use_cache_state_store():
        _cache().set(
            _cache_key(state),
            {"next_url": next_url},
            timeout=_state_ttl(),
        )
        return

    request.session[REDIRECT_SESSION_FIELD_NAME] = next_url
    request.session[OAUTH_STATE_SESSION_KEY] = state
    # Force the session to persist now.
    request.session.save()


def pop_state(request, state):

    if use_cache_state_store():
        if not state:
            return None

        key = _cache_key(state)
        data = _cache().get(key)
        if data is not None:
            _cache().delete(key)
        return data

    return request.session.pop(OAUTH_STATE_SESSION_KEY, None)
