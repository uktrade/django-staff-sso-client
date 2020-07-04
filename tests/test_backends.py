from unittest import mock

import pytest
from django.contrib.auth import get_user_model

from authbroker_client.backends import AuthbrokerBackend


@pytest.mark.django_db
@mock.patch('authbroker_client.backends.get_client')
@mock.patch('authbroker_client.backends.get_profile')
@mock.patch('authbroker_client.backends.has_valid_token')
def test_user_valid_user_create(mocked_has_valid_token, mocked_get_profile, mocked_get_client, rf):
    mocked_has_valid_token.return_value = True
    mocked_get_profile.return_value = {
        'email': 'user@test.com',
        'first_name': 'Testo',
        'last_name': 'Useri',
        'email_user_id': 'an-email_user_id@id.test.com'
    }
    AuthbrokerBackend().authenticate(request=rf)
    User = get_user_model()
    user = User.objects.get(username='an-email_user_id@id.test.com')
    assert user.first_name == 'Testo'
    assert user.last_name == 'Useri'
    assert user.email == 'user@test.com'
    assert user.username == 'an-email_user_id@id.test.com'
    assert user.has_usable_password() is False
    assert mocked_get_client.called is True
    assert mocked_get_client.call_args == mock.call(rf)
    assert mocked_get_profile.call_args == mock.call(mocked_get_client())


@pytest.mark.django_db
@mock.patch('authbroker_client.backends.get_client', mock.Mock())
@mock.patch('authbroker_client.backends.get_profile')
@mock.patch('authbroker_client.backends.has_valid_token')
def test_user_valid_user_not_create(mocked_has_valid_token, mocked_get_profile, rf):
    User = get_user_model()
    user = User(username='an-email_user_id@id.test.com', email='user@test.com', first_name='Testo', last_name='Useri')
    user.set_password('password')
    user.save()
    mocked_has_valid_token.return_value = True
    mocked_get_profile.return_value = {
        'email_user_id': 'an-email_user_id@id.test.com',
        'email': 'user@test.com',
        'first_name': 'Testo',
        'last_name': 'Useri'
    }
    AuthbrokerBackend().authenticate(request=rf)
    user = User.objects.get(username='an-email_user_id@id.test.com')
    assert user.first_name == 'Testo'
    assert user.last_name == 'Useri'
    assert user.email == 'user@test.com'
    assert user.has_usable_password() is True


@pytest.mark.django_db
@mock.patch('authbroker_client.backends.get_client', mock.Mock())
@mock.patch('authbroker_client.backends.get_profile')
@mock.patch('authbroker_client.backends.has_valid_token')
def test_use_user_uuid(mocked_has_valid_token, mocked_get_profile, settings, rf):
    User = get_user_model()
    user = User(
        username='02f673ba-7bc8-47a8-8d59-e920d78dd619', email='user@test.com',
        first_name='Testo', last_name='Useri'
    )
    user.set_password('password')
    user.save()
    mocked_has_valid_token.return_value = True
    mocked_get_profile.return_value = {
        'email_user_id': 'an-email_user_id@id.test.com',
        'user_id': '02f673ba-7bc8-47a8-8d59-e920d78dd619',
        'email': 'user@test.com',
        'first_name': 'Testo',
        'last_name': 'Useri'
    }
    settings.AUTHBROKER_USE_USER_ID_GUID = True
    AuthbrokerBackend().authenticate(request=rf)
    user = User.objects.get(username='02f673ba-7bc8-47a8-8d59-e920d78dd619')
    assert user.first_name == 'Testo'
    assert user.last_name == 'Useri'
    assert user.email == 'user@test.com'
    assert user.has_usable_password() is True


@pytest.mark.django_db
@mock.patch('authbroker_client.backends.get_client', mock.Mock())
@mock.patch('authbroker_client.backends.get_profile', mock.Mock())
@mock.patch('authbroker_client.backends.has_valid_token')
def test_invalid_user(mocked_has_valid_token, rf):
    mocked_has_valid_token.return_value = False
    assert AuthbrokerBackend().authenticate(request=rf) is None


@pytest.mark.django_db
def test_get_user_user_exists():
    User = get_user_model()
    user = User(username='an-email_user_id@id.test.com', email='user@test.com', first_name='Testo', last_name='Useri')
    user.save()
    assert AuthbrokerBackend().get_user(user.pk) == user


@pytest.mark.django_db
def test_get_user_user_doesnt_exist():
    assert AuthbrokerBackend().get_user(1) is None
