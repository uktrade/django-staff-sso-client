from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

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
        'user_id': '1234-5678-9123-4567'
    }
    AuthbrokerBackend().authenticate(request=rf)
    User = get_user_model()
    user = User.objects.get(username='1234-5678-9123-4567')
    assert user.first_name == 'Testo'
    assert user.last_name == 'Useri'
    assert user.email == 'user@test.com'
    assert user.username == '1234-5678-9123-4567'
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
    user = User(username='1234-5678-9123-4567', email='user@test.com', first_name='Testo', last_name='Useri')
    user.set_password('password')
    user.save()
    mocked_has_valid_token.return_value = True
    mocked_get_profile.return_value = {
        'user_id': '1234-5678-9123-4567',
        'email': 'user@test.com',
        'first_name': 'Testo',
        'last_name': 'Useri'
    }
    AuthbrokerBackend().authenticate(request=rf)
    user = User.objects.get(username='1234-5678-9123-4567')
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
    user = User(username='1234-5678-9123-4567', email='user@test.com', first_name='Testo', last_name='Useri')
    user.save()
    assert AuthbrokerBackend().get_user(user.pk) == user


@pytest.mark.django_db
def test_get_user_user_doesnt_exist():
    assert AuthbrokerBackend().get_user(1) is None


@pytest.mark.django_db
@mock.patch('authbroker_client.backends.get_client', mock.Mock())
@mock.patch('authbroker_client.backends.get_profile')
@mock.patch('authbroker_client.backends.has_valid_token')
def test_migrate_user_on_user_email_exists(mocked_has_valid_token, mocked_get_profile, rf, settings):
    settings.MIGRATE_EMAIL_USER_ON_LOGIN = True
    User = get_user_model()
    user = User(username='user@test.com', email='user@test.com', first_name='Testo', last_name='Useri')
    user.set_password('password')
    user.save()
    mocked_has_valid_token.return_value = True
    mocked_get_profile.return_value = {
        'user_id': '1234-5678-9123-4567',
        'email': 'user@test.com',
        'first_name': 'Testo',
        'last_name': 'Useri'
    }
    AuthbrokerBackend().authenticate(request=rf)
    user = User.objects.get(username='1234-5678-9123-4567')
    assert user.first_name == 'Testo'
    assert user.last_name == 'Useri'
    assert user.email == 'user@test.com'
    assert user.has_usable_password() is True


@pytest.mark.django_db
@mock.patch('authbroker_client.backends.get_client')
@mock.patch('authbroker_client.backends.get_profile')
@mock.patch('authbroker_client.backends.has_valid_token')
def test_migrate_user_on_user_do_not_exist(mocked_has_valid_token, mocked_get_profile, mocked_get_client, rf, settings):
    settings.MIGRATE_EMAIL_USER_ON_LOGIN = True
    mocked_has_valid_token.return_value = True
    mocked_get_profile.return_value = {
        'email': 'user@test.com',
        'first_name': 'Testo',
        'last_name': 'Useri',
        'user_id': '1234-5678-9123-4567'
    }
    AuthbrokerBackend().authenticate(request=rf)
    User = get_user_model()
    user = User.objects.get(username='1234-5678-9123-4567')
    assert user.first_name == 'Testo'
    assert user.last_name == 'Useri'
    assert user.email == 'user@test.com'
    assert user.username == '1234-5678-9123-4567'
    assert user.has_usable_password() is False
    assert mocked_get_client.called is True
    assert mocked_get_client.call_args == mock.call(rf)
    assert mocked_get_profile.call_args == mock.call(mocked_get_client())


@pytest.mark.django_db
@mock.patch('authbroker_client.backends.get_client', mock.Mock())
@mock.patch('authbroker_client.backends.get_profile')
@mock.patch('authbroker_client.backends.has_valid_token')
def test_migrate_user_on_user_email_and_user_id_exists(mocked_has_valid_token, mocked_get_profile, rf, settings):
    settings.MIGRATE_EMAIL_USER_ON_LOGIN = True
    User = get_user_model()
    # already converted user. Same id, different email
    converted_user = User(username='1234-5678-9123-4567', email='user@foo.com', first_name='Testo', last_name='Useri')
    converted_user.save()
    # not yet converted user. Same id, different email from above
    not_yet_converted_user = User(username='user@test.com', email='user@test.com', first_name='Testo',
                                  last_name='Useri')
    not_yet_converted_user.set_password('password')
    not_yet_converted_user.save()
    mocked_has_valid_token.return_value = True
    mocked_get_profile.return_value = {
        'user_id': '1234-5678-9123-4567',
        'email': 'user@test.com',
        'first_name': 'Testo',
        'last_name': 'Useri'
    }
    with pytest.raises(IntegrityError):
        AuthbrokerBackend().authenticate(request=rf)
