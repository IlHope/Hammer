from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'invite_code', 'is_active_referral']
        read_only_fields = ['invite_code', 'is_active_referral']
