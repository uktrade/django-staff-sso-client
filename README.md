# Django-staff-sso-client

[![CircleCI](https://circleci.com/gh/uktrade/django-staff-sso-client/tree/master.svg?style=svg)](https://circleci.com/gh/uktrade/django-staff-sso-client/tree/master)
[![codecov](https://codecov.io/gh/uktrade/django-staff-sso-client/branch/master/graph/badge.svg)](https://codecov.io/gh/uktrade/django-staff-sso-client)
![PyPI](https://img.shields.io/pypi/v/django-staff-sso-client.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-staff-sso-client.svg)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-staff-sso-client.svg)


A Django client for `staff-sso`


## Requirements

[Python 3.6](https://www.python.org/downloads/release/python-368/)

[Django>=2.22](https://www.djangoproject.com/)

Version 2+ of this package drops support for Django version below 2.22.

For Django versions `1.11 <= Django < 2.22` install v1.0.1:

`pip install django-staff-sso-client==1.0.1`

This client assumes your app  has either `raven` or `sentry_sdk` installed

[Raven Python](https://github.com/getsentry/raven-python)

[Sentry SDK](https://github.com/getsentry/sentry-python)


## Upgrade to version 1.0.0 considerations

From version `1.0.0` the backend populates `User.USERNAME_FIELD` with the `user_id` rather than the `email`. This is
to solve a bug affecting users with multiple email addresses.
If `MIGRATE_EMAIL_USER_ON_LOGIN` is `True`, the authentication backend tries to migrate existing users.
It is recommended to turn `MIGRATE_EMAIL_USER_ON_LOGIN` to `False` (defaults to `False`) if not needed or when all the users are migrated to avoid 
double database calls.

### What happens if two email based users are migrated to user_id?
Imagine the scenario where Testo Useri has two different email based accounts:

1) testo.user@foo.com
2) testo_user@bar.com

As soon as they login with the first one, the account is converted to `user_id`.
If they try to login with the second one, the authentication backends cannot convert the account because an account with the
same `user_id` already exists.
The authentication backends will raise an exception, **this is intended behaviour**.
 

## Installation

`pip install django-staff-sso-client`

## Configuration

Add the following to your settings file:

```
INSTALLED_APPS=[
    [...]
    'authbroker_client',
]
```

```
# authbroker config
AUTHBROKER_URL = 'speak-to-webops-team-for-access'
AUTHBROKER_CLIENT_ID = 'speak-to-webops-team-for-access'
AUTHBROKER_CLIENT_SECRET = 'speak-to-webops-team-for-access'
AUTHBROKER_STAFF_SSO_SCOPE = 'any-additional-scope-values'
```

Add the `'authbroker_client.backends.AuthbrokerBackend'` authentication backend, e.g:

```
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'authbroker_client.backends.AuthbrokerBackend',
]
```

Add the LOGIN_URL ( it must be '/auth/login' )

```
LOGIN_URL = reverse_lazy('authbroker_client:login')
```

Add the LOGIN_REDIRECT_URL for e.g.
```
LOGIN_REDIRECT_URL = reverse_lazy('home_page')
```

Then finally add this to your main `urls.py` file:

`path('auth/', include('authbroker_client.urls'))`

or, if you're using Django<2:

`url('^auth/', include('authbroker_client.urls', namespace='authbroker', app_name='authbroker_client'))`


You should now have an `/auth/login/` URL which directs users through the `staff-sso` login flow. Once a user is
authenticated via `staff-sso` (and chosen identify provider), they will be redirected back to your application.
A local django user with a matching email address will then be logged in. The user entry will be created if it does
not already exist in the database.

Once authenticated, the user will be redirected to `settings.LOGIN_REDIRECT_URL`

Use the django `@login_required` decorator to protect individual views, or if you want to protect all views use this middleware:

```
MIDDLEWARE = [
    [...]
    'authbroker_client.middleware.ProtectAllViewsMiddleware',
]
```

if you do like to use admin interface  in your app, when using this module, you will also need to install and configure the [custom_usermodel](https://github.com/uktrade/django-staff-sso-usermodel).

## Use with UKTrade mock-sso package

It is possible to configure this package to work with the [mock-sso service](https://github.com/uktrade/mock-sso).

Mock SSO requires that you provide a non-standard parameter in the query string of the initial GET call of the OAuth flow. (See the [mock-sso docs](https://github.com/uktrade/mock-sso/blob/master/README.md) for more detail.)

This parameter is called `code`. Any services which use THIS library (django-mock-sso-client) could need to undertake automated tests of a stack which uses Staff SSO for downstream components (example: testing an app which in return requires access to another service's API, both of which use SSO for authentication).

For circumstances like these you will need to prime mock-sso with this `code` parameter.

This is achieved by changing the Django settings for the app which is importing THIS library. In those settings, add:
```
TEST_SSO_PROVIDER_SET_RETURNED_ACCESS_TOKEN = 'someCode'
```
where 'someCode' will then be provided as the 'access token' during the OAuth callback to mock-sso. (Again, see the [mock-sso docs](https://github.com/uktrade/mock-sso/blob/master/README.md) for more detail.)

## TODO:

* ensure has_valid_token() checks with `staff-sso` after grace period (e.g. 1 minute)
* improve exception handling logic in `authbroker_client/views.py`
