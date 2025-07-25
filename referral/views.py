import string
import time
import random
from django.contrib.auth import get_user_model, login
from django.utils.crypto import get_random_string
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Referrals
from .serializers import UserSerializer

User = get_user_model()

def generate_unique_invite_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = get_random_string(length=length, allowed_chars=chars)
        if not User.objects.filter(invite_code=code).exists():
            return code

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(methods=['get'], detail=False, url_path='my-referrals', permission_classes=[IsAuthenticated])
    def get_referrals_list(self, request):
        referrals = Referrals.objects.filter(inviter=request.user)
        phone_numbers = [str(r.invitee.phone_number) for r in referrals]
        return Response({'referrals': phone_numbers})

class SendCodeView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')

        if not phone_number:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        user, created = User.objects.get_or_create(phone_number=phone_number, defaults={'username': phone_number})

        if created:
            user.invite_code = generate_unique_invite_code()

        code = random.randint(1000, 9999)
        user.auth_code = code
        time.sleep(2)
        user.save()

        return Response({'message': 'Code sent.', 'code': code})

class VerifyCodeView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        auth_code = request.data.get('auth_code')

        if not phone_number or not auth_code:
            return Response({'error': 'Phone number and code are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if str(auth_code) == str(user.auth_code):
            user.auth_code = None
            user.save()

            login(request, user)

            return Response({'message': 'You have successfully logged in.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'The code does not match.'}, status=status.HTTP_400_BAD_REQUEST)

class ApplyInviteCodeView(APIView):
    def post(self, request):
        invite_code = request.data.get('invite_code')
        user_id = request.data.get('id')

        if not invite_code:
            return Response({'error': 'Invite code are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active_referral:
            referral = Referrals.objects.filter(invitee=user).first()
            if referral:
                return Response({'message': 'Invite code already apolied.', 'invite_code': referral.inviter.invite_code}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Referral record missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            inviter=User.objects.get(invite_code=invite_code)
        except User.DoesNotExist:
            return Response({'error': 'Invalid invite code.'}, status=status.HTTP_400_BAD_REQUEST)

        referral = Referrals.objects.create(inviter=inviter, invitee=user)
        user.is_active_referral = True
        user.save()

        return Response({'message': 'Invite code applied successfully.'}, status=status.HTTP_200_OK)
