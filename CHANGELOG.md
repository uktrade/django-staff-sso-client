# Changelog

## [1.0.0](https://pypi.org/project/django-staff-sso-client/1.0.0/) (2019-11-20)
[Full Changelog](https://github.com/uktrade/django-staff-sso-client/pull/13/files)

**Implemented enhancements:**

- XOT-1210 Populate USERNAME_FIELD with user_id value

**Breaking changes:**

- The `UserModel.USERNAME_FIELD` will be populated with the `user_id` and not the email address anymore