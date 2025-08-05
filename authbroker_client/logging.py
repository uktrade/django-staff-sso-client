from typing import TypedDict
from django.http import HttpRequest

from django_log_formatter_asim.events import log_authentication
from django.contrib.auth.signals import user_logged_out
from authbroker_client.utils import get_client, has_valid_token


class Profile(TypedDict):
    email_user_id: str


def log_successful_login(request: HttpRequest, profile: Profile):
    log_authentication(
        request,
        event=log_authentication.Event.Logon,
        result=log_authentication.Result.Success,
        login_method=log_authentication.LoginMethod.StaffSSO,
        user={
            'username': profile['email_user_id'],
        }
    )


def log_failed_login(request: HttpRequest):
    log_authentication(
        request,
        event=log_authentication.Event.Logon,
        result=log_authentication.Result.Failure,
        login_method=log_authentication.LoginMethod.StaffSSO,
    )


def _logged_out_signal_handler(sender, request, user, **kwargs):
    # The "user session" doesn't store information on which authentication backend was used.
    # We can however, use the same `has_valid_token` mechanism to check the presence of a valid OAuth token.
    if has_valid_token(get_client(request)):
        log_authentication(
            request,
            event=log_authentication.Event.Logoff,
            result=log_authentication.Result.Success,
            login_method=log_authentication.LoginMethod.StaffSSO,
        )


def enable_logout_logging():
    user_logged_out.connect(_logged_out_signal_handler)
