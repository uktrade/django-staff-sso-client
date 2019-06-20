# Django-staff-sso-client

[![CircleCI](https://circleci.com/gh/uktrade/django-staff-sso-client/tree/master.svg?style=svg)](https://circleci.com/gh/uktrade/django-staff-sso-client/tree/master)
[![codecov](https://codecov.io/gh/uktrade/django-staff-sso-client/branch/master/graph/badge.svg)](https://codecov.io/gh/uktrade/django-staff-sso-client)
![PyPI](https://img.shields.io/pypi/v/django-staff-sso-client.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-staff-sso-client.svg)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-staff-sso-client.svg)


A Django client for `staff-sso`

## Requirements

[Python 3.6](https://www.python.org/downloads/release/python-368/)
[Django>=1.11](https://www.djangoproject.com/)

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
LOGIN_URL = reverse_lazy('authbroker:login')
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

## TODO:

* ensure has_valid_token() checks with `staff-sso` after grace period (e.g. 1 minute)
* improve exception handling logic in `authbroker_client/views.py`
