from unittest import mock
from urllib.parse import parse_qs, urlparse

from django.core.cache import cache
from django.contrib.auth import BACKEND_SESSION_KEY
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse

import pytest

from authbroker_client.utils import AUTHORISATION_URL, TOKEN_SESSION_KEY
from authbroker_client.state import OAUTH_STATE_SESSION_KEY
from authbroker_client.views import AuthCallbackView, REDIRECT_SESSION_FIELD_NAME

AUTHBROKER_BACKEND = "authbroker_client.backends.AuthbrokerBackend"


@pytest.mark.django_db
def test_auth_view(client):
    url = reverse('authbroker:login')
    response = client.get(url)
    assert response.status_code == 302
    assert AUTHORISATION_URL in response.url
    assert 'code=someCode' not in response.url


@pytest.mark.django_db
def test_auth_view_retains_next_url(client):
    url = reverse('authbroker:login') + '?next=/go-here-after-logging-in/'
    response = client.get(url)
    assert response.status_code == 302
    assert client.session[REDIRECT_SESSION_FIELD_NAME] == '/go-here-after-logging-in/'


@pytest.mark.django_db
def test_auth_view_retains_unsafe_next_url(client):
    url = reverse('authbroker:login') + '?next=https://danger.com'
    response = client.get(url)
    assert response.status_code == 302
    assert not client.session[REDIRECT_SESSION_FIELD_NAME]


@pytest.mark.django_db
def test_set_access_token_in_mock_sso(client, settings):
    settings.TEST_SSO_PROVIDER_SET_RETURNED_ACCESS_TOKEN = 'someCode'
    url = reverse('authbroker:login')
    response = client.get(url)
    assert 'code=someCode' in response.url


@pytest.mark.django_db
def test_callback_view_no_auth_code(client):
    url = reverse('authbroker:callback')
    response = client.get(url)
    assert response.status_code == 400


@pytest.mark.django_db
def test_callback_view_no_auth_state(client):
    """Redirect back to `/auth/login/` and restart the auth flow"""
    url = reverse('authbroker:callback')
    response = client.get(url, {'code': 'foo'})
    assert response.status_code == 302
    assert response.url == reverse('authbroker:login')


class StubSessionBackend(dict):
    session_key = "123"

    def is_empty(self):
        return bool(self)


@pytest.mark.django_db
@mock.patch('authbroker_client.views.get_client')
def test_callback_view_token(mocked_get_client, rf):
    mocked_get_client.return_value.fetch_token.return_value = {'token': 'test'}
    url = reverse('authbroker:callback')
    request = rf.get(url)
    request.user = AnonymousUser()
    request.session = StubSessionBackend({
        BACKEND_SESSION_KEY: AUTHBROKER_BACKEND,
        f'{TOKEN_SESSION_KEY}_oauth_state': 'state'
    })
    request.GET = {'code': 'foo'}
    response = AuthCallbackView.as_view()(request)
    assert response.status_code == 302
    assert response.url == '/'


@pytest.mark.django_db
@mock.patch('authbroker_client.views.get_client')
def test_callback_view_token_with_next_url(mocked_get_client, rf):
    mocked_get_client.return_value.fetch_token.return_value = {'token': 'test'}
    url = reverse('authbroker:callback')
    request = rf.get(url)
    request.user = AnonymousUser()
    request.session = StubSessionBackend({
        BACKEND_SESSION_KEY: AUTHBROKER_BACKEND,
        f'{TOKEN_SESSION_KEY}_oauth_state': 'state',
        REDIRECT_SESSION_FIELD_NAME: '/go-here-after-authenticating/'
    })
    request.GET = {'code': 'foo'}
    response = AuthCallbackView.as_view()(request)
    assert response.status_code == 302
    assert response.url == '/go-here-after-authenticating/'


@pytest.mark.django_db
@mock.patch('authbroker_client.views.get_client')
def test_callback_view_token_with_unsafe_next_url(mocked_get_client, rf):
    mocked_get_client.return_value.fetch_token.return_value = {'token': 'test'}
    url = reverse('authbroker:callback')
    request = rf.get(url)
    request.user = AnonymousUser()
    request.session = StubSessionBackend({
        BACKEND_SESSION_KEY: AUTHBROKER_BACKEND,
        f'{TOKEN_SESSION_KEY}_oauth_state': 'state',
        REDIRECT_SESSION_FIELD_NAME: 'https://danger.com/'
    })
    request.GET = {'code': 'foo'}
    response = AuthCallbackView.as_view()(request)
    assert response.status_code == 302
    assert response.url == '/'


@pytest.mark.django_db
@mock.patch('authbroker_client.views.get_client')
def test_callback_user_already_authenticated(mocked_get_client, rf, django_user_model):
    """Short circuit the oauth processs if the user is already authenticated"""
    mocked_get_client.return_value.fetch_token.return_value = {'token': 'test'}
    url = reverse('authbroker:callback')
    request = rf.get(url)
    request.user = django_user_model.objects.create(
        username="test",
        email="test",
        is_active=True,
    )
    request.session = StubSessionBackend({
        BACKEND_SESSION_KEY: AUTHBROKER_BACKEND,
        f'{TOKEN_SESSION_KEY}_oauth_state': 'state',
        REDIRECT_SESSION_FIELD_NAME: 'https://danger.com/'
    })
    request.GET = {'code': 'foo'}
    response = AuthCallbackView.as_view()(request)
    assert response.status_code == 302
    assert not mocked_get_client.called

# Cache based tests


def _state_key(state):
    return f'_authbroker_oauth_state_{state}'


@pytest.fixture
def use_cache(settings):
    settings.AUTHBROKER_USE_CACHE_STATE_STORE = True
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_cache_auth_view_stores_state_in_cache_not_session(client, use_cache):
    response = client.get(reverse('authbroker:login'))
    assert response.status_code == 302

    state = parse_qs(urlparse(response.url).query)['state'][0]
    # State lives in the cache, keyed by its own value
    assert cache.get(_state_key(state)) == {'next_url': None}
    # ...and NOT in the session, so concurrent flows can't clobber it.
    assert OAUTH_STATE_SESSION_KEY not in client.session


@pytest.mark.django_db
def test_cache_auth_view_stores_next_url_in_cache(client, use_cache):
    url = reverse('authbroker:login') + '?next=/go-here/'
    response = client.get(url)

    state = parse_qs(urlparse(response.url).query)['state'][0]
    assert cache.get(_state_key(state)) == {'next_url': '/go-here/'}


@pytest.mark.django_db
@mock.patch('authbroker_client.views.get_client')
def test_cache_callback_valid_state(mocked_get_client, client, use_cache):
    mocked_get_client.return_value.fetch_token.return_value = {'token': 'test'}
    cache.set(_state_key('state-A'), {'next_url': '/after/'}, 600)

    response = client.get(
        reverse('authbroker:callback'), {'code': 'foo', 'state': 'state-A'}
    )

    assert response.status_code == 302
    assert response.url == '/after/'
    # Single-use: the state is consumed on lookup.
    assert cache.get(_state_key('state-A')) is None


@pytest.mark.django_db
def test_cache_callback_unknown_state_restarts_flow(client, use_cache):
    response = client.get(
        reverse('authbroker:callback'), {'code': 'foo', 'state': 'never-issued'}
    )
    assert response.status_code == 302
    assert response.url == reverse('authbroker:login')


@pytest.mark.django_db
def test_cache_callback_no_code_is_400(client, use_cache):
    response = client.get(reverse('authbroker:callback'))
    assert response.status_code == 400


@pytest.mark.django_db
def test_cache_callback_short_circuits_when_authenticated(
    client, django_user_model, use_cache
):
    user = django_user_model.objects.create(username='someone@example.com')
    client.force_login(user, backend="authbroker_client.backends.AuthbrokerBackend")
    response = client.get(
        reverse('authbroker:callback'), {'code': 'foo', 'state': 'anything'}
    )
    assert response.status_code == 302
    assert response.url != reverse('authbroker:login')


@pytest.mark.django_db
@mock.patch('authbroker_client.views.get_client')
def test_cache_concurrent_flows_both_resolve(mocked_get_client, client, use_cache):
    """Test multiple flows can run concurrently without clobbering the state key."""
    mocked_get_client.return_value.fetch_token.return_value = {'token': 'test'}
    cache.set(_state_key('A'), {'next_url': '/a/'}, 600)
    cache.set(_state_key('B'), {'next_url': '/b/'}, 600)

    callback = reverse('authbroker:callback')
    r1 = client.get(callback, {'code': 'c1', 'state': 'A'})
    r2 = client.get(callback, {'code': 'c2', 'state': 'B'})

    assert r1.url == '/a/'
    assert r2.url == '/b/'


@pytest.mark.django_db
@mock.patch("authbroker_client.views.authenticate")
@mock.patch("authbroker_client.views.get_client")
def test_callback_redirects_when_existing_session_for_different_backend_user(
    mocked_get_client,
    mocked_authenticate,
    client,
    django_user_model,
    settings,
):
    settings.AUTHBROKER_USE_CACHE_STATE_STORE = False
    settings.LOGIN_REDIRECT_URL = "/default/redirect/url"
    settings.AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
        AUTHBROKER_BACKEND,
    ]
    existing_admin_user = django_user_model.objects.create_user(
        username="admin@example.com",
        email="admin@example.com",
    )
    sso_user = django_user_model.objects.create_user(
        username="someone@example.com",
        email="someone@example.com",
    )
    client.force_login(
        existing_admin_user,
        backend="django.contrib.auth.backends.ModelBackend",
    )
    # sanity check
    assert client.session[BACKEND_SESSION_KEY] == "django.contrib.auth.backends.ModelBackend"
    mocked_get_client.return_value.authorization_url.return_value = (
        "https://sso.example.com/o/authorize/?state=state-A",
        "state-A",
    )
    mocked_get_client.return_value.fetch_token.return_value = {"token": "test"}
    sso_user.backend = AUTHBROKER_BACKEND
    mocked_authenticate.return_value = sso_user

    login_response = client.get(
        reverse("authbroker:login"),
        {"next": "/session/redirect/url"},
    )

    assert login_response.status_code == 302
    assert client.session[REDIRECT_SESSION_FIELD_NAME] == "/session/redirect/url"

    callback_response = client.get(
        reverse("authbroker:callback"),
        {
            "code": "foo",
            "state": "state-A",
        },
    )

    assert callback_response.status_code == 302
    assert callback_response.url == "/session/redirect/url"
    assert callback_response.url != settings.LOGIN_REDIRECT_URL
    assert client.session[BACKEND_SESSION_KEY] == AUTHBROKER_BACKEND
