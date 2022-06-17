from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from django.urls import resolve, reverse


class ProtectAllViewsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.anonymous_paths = getattr(
            settings,
            "AUTHBROKER_ANONYMOUS_PATHS",
            (),
        )
        self.anonymous_url_names = getattr(
            settings,
            "AUTHBROKER_ANONYMOUS_URL_NAMES",
            (),
        )

    @staticmethod
    def get_redirect_url(request):
        params = {
            REDIRECT_FIELD_NAME: request.get_full_path(),
        }

        querystring = urlencode(params)

        redirect_url = reverse("authbroker_client:login")

        return redirect(f"{redirect_url}?{querystring}")

    def __call__(self, request):
        if not request.user.is_authenticated:
            resolved_path = resolve(request.path)
            is_anonymous_path = request.path in self.anonymous_paths
            is_anonymous_url_name = resolved_path.url_name in self.anonymous_url_names
            is_authbroker_client_path = resolved_path.app_name == "authbroker_client"

            if (
                not is_anonymous_path
                and not is_anonymous_url_name
                and not is_authbroker_client_path
            ):
                return self.get_redirect_url(request)

        response = self.get_response(request)
        return response
