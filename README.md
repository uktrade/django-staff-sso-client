# Django-staff-sso-client

NOTE: this project is still very much WIP

# Overview

A Django client for `staff-sso`

# Installation

`pip install -e git+https://github.com/uktrade/django-staff-sso-client.git#egg=authbroker_client`

# Configuration

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
AUTHBROKER_SCOPES = 'read write'
```

Add the `'authbroker_client.backends.AuthbrokerBackend'` authentication backend, e.g:

```
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'authbroker_client.backends.AuthbrokerBackend',
]
```

Then finally add this to your main `urls.py` file:

`    path('auth/', include('authbroker_client.urls', namespace='authbroker')),`


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

# TODO:

* add some tests
* ensure has_valid_token() checks with `staff-sso` after grace period (e.g. 1 minute)
* improve exception handling logic in `authbroker_client/views.py`
