# Changelog

## [4.2.3](https://pypi.org/project/django-staff-sso-client/4.2.2/) (2024-02-21)

- Added support for Django 5

## [4.2.2](https://pypi.org/project/django-staff-sso-client/4.2.2/) (2024-02-21)
[Full Changelog](https://github.com/uktrade/django-staff-sso-client/pull/37/)

- Bump Django to 4.2.10 minimum

## [4.2.1](https://pypi.org/project/django-staff-sso-client/4.2.1/) (2023-10-02)

**Fixed bugs:**

- Fix overly-restrictive Django version requirement

## [4.2.0](https://pypi.org/project/django-staff-sso-client/4.2.0/) (2023-05-23)

**Implemented enhancements:**

- Add support for Django 4.2

## [4.1.1](https://pypi.org/project/django-staff-sso-client/4.1.1/) (2022-11-18)

**Implemented enhancements:**

- Add support for Django 4.1

## [4.0.1](https://pypi.org/project/django-staff-sso-client/4.0.1/) (2022-06-21)

**Implemented enhancements:**

- Add ability to mark URL names as anonymous.

## [4.0.0](https://pypi.org/project/django-staff-sso-client/4.0.0/) (2022-04-12)

**Implemented enhancements:**

- Add support for Django 4
- Add support for Python 3.10
- Modernise how distributions are generated

**Breaking changes:**

- Dropped support for Django 2.2
- Dropped support for Python 3.6

## [3.1.1](https://pypi.org/project/django-staff-sso-client/3.1.1/) (2021-09-30)

[Full Changelog](https://github.com/uktrade/django-staff-sso-client/pull/26/files)

**Implemented enhancements**

- Include the source distribution when uploading to pypi

## [3.1.0](https://pypi.org/project/django-staff-sso-client/3.1.0/) (2020-08-24)

[Full Changelog](https://github.com/uktrade/django-staff-sso-client/pull/22/files)

**Implemented enhancements**

- Corretly handle the ?next= querystring paramer and redirect to it, after the user authenticates

## [3.0.0](https://pypi.org/project/django-staff-sso-client/3.0.0/) (2020-08-24)

[Full Changelog](https://github.com/uktrade/django-staff-sso-client/pull/22/files)

**Implemented enhancements:**

- The default ID field has been changed to `email_user_id` [previously the `user_id` UUID field was the default]

- There is now an option to change the profile -> user instance field mapping on user creation.

- `MIGRATE_EMAIL_USER_ON_LOGIN` logic has been removed.

## [2.1.0](https://pypi.org/project/django-staff-sso-client/2.1.0/) (2020-03-25)

[Full Changelog](https://github.com/uktrade/django-staff-sso-client/pull/18/files)

**Implemented enhancements:**

- No ticket - Add option to specify additional scope values

## [2.0.0](https://pypi.org/project/django-staff-sso-client/2.0.0/) (2020-03-03)

[Full Changelog](https://github.com/uktrade/django-staff-sso-client/pull/16/files)

**Fixed bugs:**

- No ticket - Added support for Django 3.0.3 and dropped support

**Breaking changes:**

- Dropped support for Django < 2.22

## [1.0.1](https://pypi.org/project/django-staff-sso-client/1.0.1/) (2019-12-19)

[Full Changelog](https://github.com/uktrade/django-staff-sso-client/pull/14/files)

**Fixed bugs:**

- No ticket - Handle usage of sentry_sdk instead of legacy raven

## [1.0.0](https://pypi.org/project/django-staff-sso-client/1.0.0/) (2019-11-20)

[Full Changelog](https://github.com/uktrade/django-staff-sso-client/pull/13/files)

**Implemented enhancements:**

- XOT-1210 - Populate USERNAME_FIELD with user_id value

**Breaking changes:**

- The `UserModel.USERNAME_FIELD` will be populated with the `user_id` and not the email address anymore
