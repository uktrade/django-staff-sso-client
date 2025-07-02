from unittest import mock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls.exceptions import Resolver404

from authbroker_client.middleware import ProtectAllViewsMiddleware


def get_response_fake(request):
    return "the-public-view"


@pytest.mark.django_db
class ProtectAllViewsMiddelwareTestCase(TestCase):
    def setUp(self):
        factory = RequestFactory()
        self.request = factory.get("/")
        self.request.user = AnonymousUser()

    def test_no_settings(self):
        middleware = ProtectAllViewsMiddleware(get_response=get_response_fake)
        response = middleware(request=self.request)

        assert response.status_code == 302
        assert response.url == "/auth/login/?next=%2F"

    @mock.patch(
        "authbroker_client.middleware.settings", AUTHBROKER_ANONYMOUS_PATHS=("/",)
    )
    @mock.patch("authbroker_client.middleware.redirect")
    def test_anonymous_path(self, redirect, settings):
        middleware = ProtectAllViewsMiddleware(get_response=get_response_fake)
        response = middleware(request=self.request)

        assert not redirect.called
        assert response == "the-public-view"

    @mock.patch(
        "authbroker_client.middleware.settings",
        AUTHBROKER_ANONYMOUS_URL_NAMES=("home",),
    )
    @mock.patch("authbroker_client.middleware.redirect")
    def test_anonymous_path_name(self, redirect, settings):
        middleware = ProtectAllViewsMiddleware(get_response=get_response_fake)
        response = middleware(request=self.request)

        assert not redirect.called
        assert response == "the-public-view"

    @mock.patch(
        "authbroker_client.middleware.settings",
        AUTHBROKER_ANONYMOUS_URL_NAMES=("home",),
    )
    def test_unresolved_path(self, settings):
        unresolved_path_request = RequestFactory().get("/not.a.real.path")
        unresolved_path_request.user = AnonymousUser()
        middleware = ProtectAllViewsMiddleware(get_response=get_response_fake)

        response = middleware(request=unresolved_path_request)

        assert response.status_code == 302
        assert response.url == "/auth/login/?next=%2Fnot.a.real.path"

    @mock.patch(
        "authbroker_client.middleware.settings", AUTHBROKER_ANONYMOUS_PATHS=("/not.a.real.path",)
    )
    @mock.patch("authbroker_client.middleware.redirect")
    def test_unresolved_anonymous_path(self, redirect, settings):
        unresolved_path_request = RequestFactory().get("/not.a.real.path")
        unresolved_path_request.user = AnonymousUser()
        middleware = ProtectAllViewsMiddleware(get_response=get_response_fake)

        with pytest.raises(Resolver404):
            response = middleware(request=unresolved_path_request)
            assert not redirect.called
            assert response == "the-public-view"
