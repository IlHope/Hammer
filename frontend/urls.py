from django.urls import path
from .views import auth_view, verify_code_view, profile_view

urlpatterns = [
    path('auth/', auth_view, name='auth'),
    path('verify/', verify_code_view, name='verify'),
    path('profile/', profile_view, name='profile'),
]