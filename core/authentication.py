from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class MobileBackend(ModelBackend):

    def authenticate(self, request, mobile=None, password=None, **kwargs):

        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        return None