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
            return self.get_or_create_user(profile)
        return None

    def get_or_create_user(self, profile):
        id_key = self.get_profile_id_name()

        user, created = UserModel.objects.get_or_create(
            **{UserModel.USERNAME_FIELD: profile[id_key]},
            defaults=self.user_create_mapping(profile),
        )

        if created:
            user.set_unusable_password()
            user.save()
        return user

    def user_create_mapping(self, profile):
        return {
            'email': profile['email'],
            'first_name': profile['first_name'],
            'last_name': profile['last_name'],
        }

    @staticmethod
    def get_profile_id_name():
        """Return the key name for the ID field in the user profile.  This defaults to
        `email_user_id`, with the option to set it to the `user_id`/guid field.
        """
        if getattr(settings, 'AUTHBROKER_USE_USER_ID_GUID', False):
            return 'user_id'

        return 'email_user_id'

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
