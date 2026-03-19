# adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.urls import reverse

# adapters.py
class NoSocialLoginAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        email = sociallogin.user.email

        if not email:
            return

        from django.contrib.auth import get_user_model
        User = get_user_model()

        if User.objects.filter(email=email).exists():
            raise ImmediateHttpResponse(redirect("login"))

        # Stash Google data in session for manual signup
        request.session["google_prefill"] = {
            "email": sociallogin.user.email,
            "first_name": sociallogin.user.first_name,
            "last_name": sociallogin.user.last_name,
            "uid": sociallogin.account.uid,
            "provider": sociallogin.account.provider,
        }

        # Stop allauth from creating a user
        raise ImmediateHttpResponse(redirect("register"))

