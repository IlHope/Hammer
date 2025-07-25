from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import UserViewSet, SendCodeView, VerifyCodeView, ApplyInviteCodeView

router = DefaultRouter()
router.register(r'profile', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('send-code/', SendCodeView.as_view(), name='send-code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    path('apply-invite/', ApplyInviteCodeView.as_view(), name='apply-invite'),
]