# Changelog

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