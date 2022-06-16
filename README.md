# Django-staff-sso-client

[![CircleCI](https://circleci.com/gh/uktrade/django-staff-sso-client/tree/master.svg?style=svg)](https://circleci.com/gh/uktrade/django-staff-sso-client/tree/master)
[![codecov](https://codecov.io/gh/uktrade/django-staff-sso-client/branch/master/graph/badge.svg)](https://codecov.io/gh/uktrade/django-staff-sso-client)
![PyPI](https://img.shields.io/pypi/v/django-staff-sso-client.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-staff-sso-client.svg)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-staff-sso-client.svg)


A Django client for `staff-sso`


## Requirements

[Python 3.7](https://www.python.org/downloads/release/python-370/)

[Django>=3.2](https://www.djangoproject.com/)

Version 4+ of this package drops support for Django version 2.2.

For Django versions `Django==2.2` install v3.1.1:

`pip install django-staff-sso-client==3.1.1`

Version 2+ of this package drops support for Django versions below 2.2.

For Django versions `1.11 <= Django < 2.2` install v1.0.1:

`pip install django-staff-sso-client==1.0.1`

This client assumes your app  has either `raven` or `sentry_sdk` installed

[Raven Python](https://github.com/getsentry/raven-python)

[Sentry SDK](https://github.com/getsentry/sentry-python)


## Upgrade to version 3.0.0 considerations

The default ID field has been changed to `email_user_id`. Previously the `user_id` (guid) was the default field - see below for details on how to revert to `user_id` if needed.

`MIGRATE_EMAIL_USER_ON_LOGIN` logic has been removed.

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
AUTHBROKER_ANONYMOUS_PATHS = (Tuple/list of paths that should be unprotected)
AUTHBROKER_ANONYMOUS_URL_NAMES = (list of url names that should be unprotected)
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

## Change the default user id field

Staff-sso maintains two unique user ids for each user: the `email_user_id` field, which is in an email format [NOTE: it is purely a unique id, not a valid email address] and the `user_id` field, which is a GUID.  By default (from version 3.0.0 onwards) django-staff-sso-client identifies users based on the `email_user_id` field.  This is the preferred option for most cases.  If however, you need to use the `user_id` field, then add this to your settings.py file:

```
AUTHBROKER_USE_USER_ID_GUID = True
```

When creating new users django-staff-sso-client attempts to store the user id in the `User.USERNAME_FIELD` field.  With the stock django model this will be the `username` field.  If you use a custom user model you can override this field as needed, for example:

```
class YourCustomUserModel(...):
  USERNAME_FIELD = 'sso_email_id'
```

NOTE: As per django's documentation, the `USERNAME_FIELD` should be the user model's primary key.

## Change the user creation mapping

Here's an example staff-sso profile, which is available at the point of user creation:

```
{
    'user_id': '6fa3b542-9a6f-4fc3-a248-168596572999',   
    'email_user_id': 'john.smith-6fa3b542@id.trade.gov.uk',    
    'email': 'john.smith@someplace.gov.uk',
    'contact_email': 'john.smith@someemail.com',
    'related_emails': [   'jsmith@someotherplace.com',
                          'me@johnsmith.com'],  
    'first_name': 'John',
    'last_name': 'Smith',                
    'groups': [ ... ],                    
    'permitted_applications': [ ... ],
    'access_profiles': [ ... ]
}
```

The default mapping is:

```
{
      'email': profile['email'],
      'first_name': profile['first_name'],
      'last_name': profile['last_name'],
}
```

You can change this default mapping by subclassing the authentication backend `authbroker_client.backends.AuthbrokerBackend` and overriding the `user_create_mapping` method.

Here's an example:

```
from authbroker_client.backends import AuthbrokerBackend


class CustomAuthbrokerBackend(AuthbrokerBackend):
    def user_create_mapping(self, profile):
        return {
            "is_active": True,
            "first_name": profile["first_name"],
            "last_name": profile["last_name"],
        }
```

### Exclude page from SSO Auth check

In order to allow anonymous access to a page on a site protected using this client, add the following setting to your Django settings file:

```
AUTHBROKER_ANONYMOUS_PATHS = ('anonymous/path',)
```

Alternatively, you can use the `AUTHBROKER_ANONYMOUS_URL_NAMES` setting to specify a list of url names.
```
AUTHBROKER_ANONYMOUS_URL_NAMES = ('url-name',)
```

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
