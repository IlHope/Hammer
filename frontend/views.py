from django.shortcuts import render, redirect
from referral.models import Referrals
from django.contrib import messages
from django.contrib.auth import get_user_model
import random
import time
from referral.views import generate_unique_invite_code

User = get_user_model()

def auth_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        if phone_number:
            user, created = User.objects.get_or_create(phone_number=phone_number,  defaults={'username': phone_number})
            if created:
                user.invite_code = generate_unique_invite_code()

            code = random.randint(1000, 9999)
            user.auth_code = code
            time.sleep(2)
            user.save()

            request.session['phone_number'] = phone_number
            return redirect('verify')
    return render(request, 'auth.html')

def verify_code_view(request):
    if request.method == 'POST':
        code = request.POST.get('auth_code')
        phone_number = request.session.get('phone_number')

        if not phone_number:
            return redirect('auth')

        try:
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return redirect('auth')

        if str(user.auth_code) == str(code):
            user.auth_code = None
            user.save()
            request.session['user_id'] = user.id
            return redirect('profile')
        else:
            messages.error(request, 'Неверный код. Попробуйте снова.')

    return render(request, 'verify.html')

def profile_view(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('auth')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('auth')

    if request.method == 'POST' and request.POST.get('form_name') == 'invite_code_form':
        invite_code = request.POST.get('invite_code')
        if invite_code:
            if user.is_active_referral:
                messages.info(request, 'Вы уже ввели инвайт-код.')
            else:
                try:
                    inviter = User.objects.get(invite_code=invite_code)
                    Referrals.objects.create(inviter=inviter, invitee=user)
                    user.is_active_referral = True
                    user.save()
                    messages.success(request, 'Инвайт-код успешно применён!')
                except User.DoesNotExist:
                    messages.error(request, 'Неверный инвайт-код.')

    referral = Referrals.objects.filter(invitee=user).select_related('inviter').first()
    inviter_code = referral.inviter.invite_code if referral else None

    referrals = Referrals.objects.filter(inviter=user).values_list('invitee__phone_number', flat=True)

    return render(request, 'profile.html', {
        'phone_number': user.phone_number,
        'invite_code': user.invite_code,
        'referrals': referrals,
        'inviter_code': inviter_code,
        'show_invite_form': not user.is_active_referral,
    })
