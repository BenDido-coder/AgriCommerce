from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, email=None, phone=None, password=None, **kwargs):
        try:
            if email:
                user = User.objects.get(email=email)
            elif phone:
                user = User.objects.get(phone=phone)
            else:
                return None
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None