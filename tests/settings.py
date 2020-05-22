SECRET_KEY = 'fake-key'

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.admin',
    'authbroker_client',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ROOT_URLCONF = 'tests.urls'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'authbroker_client.backends.AuthbrokerBackend',
]

LOGIN_URL = 'authbroker:login'
LOGIN_REDIRECT_URL = 'home'


# authbroker config
AUTHBROKER_URL = 'https://test.com'
AUTHBROKER_CLIENT_ID = 'debug'
AUTHBROKER_CLIENT_SECRET = 'debug'
AUTHBROKER_STAFF_SSO_SCOPE = 'additional-scope'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'authbroker_client.middleware.ProtectAllViewsMiddleware',
]


SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'

# For integration with https://github.com/uktrade/mock-sso
# mock-sso requires you to provide a `code` param in the initial
# GET /o/authorize query string. It passes this param straight back out
# during the POST /o/token call. (`code` param is basically used as
# a 'fixture' setup for the token call). An app which uses this lib
# (django-staff-sso-client) will likely want to be able to test
# against mock-sso and so we include this slightly hacky bit of setup
# here.
#
# Set this to the 'access_token' you'd like returned when your user's
# session calls the token endpoint
TEST_SSO_PROVIDER_SET_RETURNED_ACCESS_TOKEN = None
