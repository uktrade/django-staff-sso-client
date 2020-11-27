from unittest import mock

import pytest

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.test.client import RequestFactory

from authbroker_client.middleware import ProtectAllViewsMiddleware


def get_response_fake(request):
    return "the-public-view"


@pytest.mark.django_db
class ProtectAllViewsMiddelwareTestCase(TestCase):
    def setUp(self):
        factory = RequestFactory()
        self.request = factory.get("/")
        self.request.user = AnonymousUser()

    @mock.patch('authbroker_client.middleware.settings', AUTHBROKER_ANONYMOUS_PATHS=())
    def test_no_anonymous_paths(self, settings):
        middleware = ProtectAllViewsMiddleware(get_response=get_response_fake)

        response = middleware(request=self.request)
        assert response.status_code == 302

        assert response.url == "/auth/login/?next=%2F"

    @mock.patch('authbroker_client.middleware.settings', AUTHBROKER_ANONYMOUS_PATHS=("/",))
    @mock.patch('authbroker_client.middleware.redirect')
    def test_anonymous_path(self, redirect, settings):
        middleware = ProtectAllViewsMiddleware(get_response=get_response_fake)
        response = middleware(request=self.request)

        assert not redirect.called
        assert response == "the-public-view"
