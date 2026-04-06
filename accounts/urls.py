
from django.urls import include, path
from django.shortcuts import render
from .views import register_view, login_view, logout_view,profile_view,change_password
from django.contrib import admin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
   path('change-password/',change_password, name='change_password'),
    path('register/',register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
     path('profile/',profile_view, name='profile'),
     
    path('reset-password/', PasswordResetView.as_view(template_name='forgot-password.html'), name='reset_password'),
    path('reset-password/done/', PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset-password/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='reset-password.html'), name='password_reset_confirm'),
    path('reset-password/complete/', PasswordResetCompleteView.as_view(template_name='password-successful.html'), name='password_reset_complete'),
   
    path('claim/',lambda request: render(request, 'claim.html'), name='claim'),
]