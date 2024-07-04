from allauth.account.auth_backends import AuthenticationBackend
from django_otp import verify_token


class TwoFactorAllAuthBackend(AuthenticationBackend):
    def authenticate(self, request, **kwargs):
        user = super().authenticate(request, **kwargs)
        if user and user.is_authenticated:
            otp_token = kwargs.get('otp_token')
            if otp_token:
                device = verify_token(user=user, token=otp_token)
                if device:
                    return user
            elif not user.totpdevice_set.exists():
                # If user doesn't have 2FA set up, allow login
                return user
        return None
