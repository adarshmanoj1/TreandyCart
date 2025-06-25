from django.contrib.auth.backends import BaseBackend
from core.models import User
from django.contrib.auth.backends import ModelBackend


class PhoneBackend(BaseBackend):
    def authenticate(self, request, phone=None, **kwargs):
        try:
            return User.objects.get(phone=phone)
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class PhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        print(f"Trying login with {username}")
        try:
            user = User.objects.get(phone=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
