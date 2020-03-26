from unittest import mock

import requests_mock
from django.conf import settings
from django.http import HttpResponseRedirect
from requests_oauthlib import OAuth2Session

from authbroker_client.utils import (
    get_profile,
    has_valid_token,
    get_client,
    get_scope,
    authbroker_login_required,
)


def test_has_valid_token(mocked_oauth_client):
    mocked_oauth_client.authorized = True
    assert has_valid_token(mocked_oauth_client) is True


def test_get_profile():
    with requests_mock.Mocker() as m:
        m.get('https://test.com/api/v1/user/me/', json={'a': 'b'})
        token = {
            'access_token': 'eswfld123kjhn1v5423',
            'refresh_token': 'asdfkljh23490sdf',
            'token_type': 'Bearer',
            'expires_in': '30',
        }
        mock_request = mock.Mock(session={'_authbroker_token': token})
        mock_request.build_absolute_uri.return_value = 'https://test.com'
        client = get_client(request=mock_request)
        assert get_profile(client) == {'a': 'b'}


def test_get_client():
    token = {
        'access_token': 'eswfld123kjhn1v5423',
        'refresh_token': 'asdfkljh23490sdf',
        'token_type': 'Bearer',
        'expires_in': '30',
    }
    mock_request = mock.Mock(session={'_authbroker_token': token})
    mock_request.build_absolute_uri.return_value = 'https://test.com'
    client = get_client(request=mock_request)
    assert isinstance(client, OAuth2Session)
    assert client.scope == get_scope()
    assert client.client_id == settings.AUTHBROKER_CLIENT_ID
    assert client.token == token


@mock.patch('authbroker_client.utils.get_client', mock.Mock())
@mock.patch('authbroker_client.utils.has_valid_token')
def test_authbroker_login_required_allowed_decorator(mocked_has_valid_token):
    mocked_has_valid_token.return_value = True
    func = mock.Mock()
    mocked_request = mock.Mock()
    decorated_func = authbroker_login_required(func)
    response = decorated_func(mock.Mock())
    assert response == func(mocked_request)


@mock.patch('authbroker_client.utils.get_client', mock.Mock())
@mock.patch('authbroker_client.utils.has_valid_token')
def test_authbroker_login_required_not_allowed_decorator(mocked_has_valid_token):
    mocked_has_valid_token.return_value = False
    func = mock.Mock()
    decorated_func = authbroker_login_required(func)
    response = decorated_func(mock.Mock())
    assert response.status_code == 302
    assert response.url == '/auth/login/'
    assert isinstance(response, HttpResponseRedirect)


def test_settings_override_scope(settings):
    token = {
        'access_token': 'eswfld123kjhn1v5423',
        'refresh_token': 'asdfkljh23490sdf',
        'token_type': 'Bearer',
        'expires_in': '30',
    }

    new_scope = 'read write data-hub:internal-front-end'

    settings.AUTHBROKER_STAFF_SSO_SCOPE = new_scope

    mock_request = mock.Mock(session={'_authbroker_token': token})
    mock_request.build_absolute_uri.return_value = 'https://test.com'
    client = get_client(request=mock_request,)
    assert isinstance(client, OAuth2Session)
    assert client.scope == new_scope
