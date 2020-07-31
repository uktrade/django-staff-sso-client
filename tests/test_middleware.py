from unittest import mock

import pytest

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, Client
from django.test.client import RequestFactory

from authbroker_client.middleware import ProtectAllViewsMiddleware


def get_response_fake(request):
    return True


@pytest.mark.django_db
class AnonymousUserAccessibilityTests(TestCase):
    def setUp(self):
        factory = RequestFactory()
        self.request = factory.get('/')
        self.request.user = AnonymousUser()

    @mock.patch('authbroker_client.middleware.settings', AUTHBROKER_ANONYMOUS_PATHS=())
    @mock.patch('authbroker_client.middleware.redirect')
    def test_no_anonymous_paths(self, redirect, settings):
        middleware = ProtectAllViewsMiddleware(get_response=get_response_fake)

        middleware(request=self.request)
        redirect.assert_called_once_with("authbroker_client:login")

    @mock.patch('authbroker_client.middleware.settings', AUTHBROKER_ANONYMOUS_PATHS=("/", ))
    @mock.patch('authbroker_client.middleware.redirect')
    def test_anonymous_path(self, redirect, settings):
        middleware = ProtectAllViewsMiddleware(get_response=get_response_fake)

        outcome = middleware(request=self.request)
        assert not redirect.called
        assert outcome

