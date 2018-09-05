# Django-staff-sso-client

NOTE: this project is still very much WIP

# Overview

A Django client for `staff-sso`

# Installation

`pip install ...`

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
AUTHBROKER_URL = 'speak-to-webops'
AUTHBROKER_CLIENT_ID = 'speak-to-webops'
AUTHBROKER_CLIENT_SECRET = 'speak-to-webops'
AUTHBROKER_SCOPES = 'read write'
```

Add to your main `urls.py` file:

`path('auth/', include('authbroker_client.urls')),`

You should now have an `/auth/login/` URL which directs users through the `staff-sso` login flow. Once a user is
authenticated via `staff-sso` (and chosen identify provider), they will be redirected back to your application.
A local django user with a matching email address will then be logged in. The user entry will be created if it does
not already exist in the database.

Use the django `@login_required` decorator to protect your views.
