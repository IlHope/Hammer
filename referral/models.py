from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractUser):
    phone_number = PhoneNumberField(unique=True)
    invite_code = models.CharField(max_length=6, unique=True)
    is_active_referral = models.BooleanField(default=False)
    auth_code = models.PositiveSmallIntegerField(blank=True, null=True)

class Referrals(models.Model):
    inviter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='inviters')
    invitee = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='invitees')