from unittest import mock

from django.urls import reverse
import pytest

from authbroker_client.utils import AUTHORISATION_URL, TOKEN_SESSION_KEY
from authbroker_client.views import AuthCallbackView


@pytest.mark.django_db
def test_auth_view(client):
    url = reverse('authbroker:login')
    response = client.get(url)
    assert response.status_code == 302
    assert AUTHORISATION_URL in response.url
    assert 'code=someCode' not in response.url


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
    url = reverse('authbroker:callback')
    response = client.get(url, {'code': 'foo'})
    assert response.status_code == 500


@pytest.mark.django_db
@mock.patch('authbroker_client.views.get_client')
def test_callback_view_token(mocked_get_client, rf):
    mocked_get_client.return_value.fetch_token.return_value = {'token': 'test'}
    url = reverse('authbroker:callback')
    request = rf.get(url)
    request.session = {f'{TOKEN_SESSION_KEY}_oauth_state': 'state'}
    request.GET = {'code': 'foo'}
    response = AuthCallbackView.as_view()(request)
    assert response.status_code == 302
