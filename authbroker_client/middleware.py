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
            'AUTHBROKER_ANONYMOUS_PATHS',
            (),
        )

    @staticmethod
    def get_redirect_url(request):
        params = {
            REDIRECT_FIELD_NAME: request.get_full_path(),
        }

        querystring = urlencode(params)

        redirect_url = reverse('authbroker_client:login')

        return redirect(f"{redirect_url}?{querystring}")

    def __call__(self, request):
        if (
            request.path not in self.anonymous_paths
            and resolve(request.path).app_name != "authbroker_client"  # noqa: W503
            and not request.user.is_authenticated  # noqa: W503
        ):
            return self.get_redirect_url(request)

        response = self.get_response(request)
        return response
