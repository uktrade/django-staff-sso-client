import logging
from django.conf import settings
from django.contrib.auth import get_user_model
from authbroker_client.utils import get_client, has_valid_token, get_profile


logger = logging.getLogger('authbroker-client')
UserModel = get_user_model()


class AuthbrokerBackend:
    def authenticate(self, request, **kwargs):
        client = get_client(request)
        if has_valid_token(client):
            profile = get_profile(client)
            if getattr(settings, 'MIGRATE_EMAIL_USER_ON_LOGIN', False):
                if self.user_email_exists(profile):
                    user = self.migrate_username_from_email_to_id(profile)
                else:
                    user = self.get_or_create_user(profile)
            else:
                user = self.get_or_create_user(profile)
            return user
        return None

    @staticmethod
    def user_email_exists(profile):
        return UserModel.objects.filter(**{UserModel.USERNAME_FIELD: profile['email']}).exists()

    @staticmethod
    def migrate_username_from_email_to_id(profile):
        user = UserModel.objects.get(**{UserModel.USERNAME_FIELD: profile['email']})
        setattr(user, UserModel.USERNAME_FIELD, profile['user_id'])
        user.save()
        return user

    @staticmethod
    def get_or_create_user(profile):
        user, created = UserModel.objects.get_or_create(
            **{UserModel.USERNAME_FIELD: profile['user_id']},
            defaults={
                'email': profile['email'],
                'first_name': profile['first_name'],
                'last_name': profile['last_name']
            })
        if created:
            user.set_unusable_password()
            user.save()
        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
