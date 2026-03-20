from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random
from django.utils import timezone

class UserManager(BaseUserManager):

    def create_user(self, mobile, first_name, last_name, password=None):
        if not mobile:
            raise ValueError("Mobile number is required")

        user = self.model(
            mobile=mobile,
            first_name=first_name,
            last_name=last_name
        )

        user.set_password(password)  # hashes password
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    data_balance = models.IntegerField(default=1000)  # in MB
    mobile = models.CharField(max_length=15, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.mobile
    
class OTPVerification(models.Model):

    mobile = models.CharField(max_length=15)
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp():
        return str(random.randint(100000, 999999))

    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 300