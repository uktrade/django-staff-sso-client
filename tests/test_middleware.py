from unittest import mock

import pytest

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, Client
from django.test.client import RequestFactory

from authbroker_client.middleware import ProtectAllViewsMiddleware


class resolve_mock():
    def resolve(self):
        return "url_name"

    @property
    def app_name(self):
        return "app_name"


def get_response_fake(request):
    return True


@pytest.mark.django_db
class AnonymousUserAccessibilityTests(TestCase):
    def setUp(self):
        factory = RequestFactory()
        self.request = factory.get('/')
        self.request.user = AnonymousUser()
        self.app_name = 'test'

    @mock.patch('authbroker_client.middleware.settings', AUTHBROKER_ANONYMOUS_PATHS='')
    @mock.patch('authbroker_client.middleware.redirect')
    def test_no_anonymous_paths(self, redirect, settings):
        middleware = ProtectAllViewsMiddleware(get_response=get_response_fake)

        middleware(request=self.request)
        redirect.assert_called_once_with("authbroker_client:login")

    @mock.patch('authbroker_client.middleware.settings', AUTHBROKER_ANONYMOUS_PATHS="url_name")
    @mock.patch('authbroker_client.middleware.redirect')
    @mock.patch('authbroker_client.middleware.resolve')
    def test_anonymous_path(self, resolve, redirect, settings):
        resolve.return_value = resolve_mock.resolve(self.app_name)
        middleware = ProtectAllViewsMiddleware(get_response=get_response_fake)

        outcome = middleware(request=self.request)
        assert outcome

