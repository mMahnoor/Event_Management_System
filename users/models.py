from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.

class CustomUser(AbstractUser):
    profile_image = models.ImageField(
        upload_to='occavue_profile_images/', blank=True, default='media/occavue_profile_images/default_m4xs9f')
    phone = PhoneNumberField(blank=True)

    def __str__(self):
        return self.username
