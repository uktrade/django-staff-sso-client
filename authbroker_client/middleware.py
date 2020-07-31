from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve


class ProtectAllViewsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.anonymous_paths = getattr(
            settings,
            'AUTHBROKER_ANONYMOUS_PATHS',
            (),
        )

    def __call__(self, request):
        if (
            request.path not in self.anonymous_paths and  # noqa W504
            resolve(request.path).app_name != 'authbroker_client' and not
            request.user.is_authenticated
        ):
            return redirect('authbroker_client:login')

        response = self.get_response(request)
        return response
