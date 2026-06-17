from rest_framework.permissions import BasePermission


class IsMFAVerified(BasePermission):
    """
    Permission class that checks if the user has completed MFA if it's enabled for them.
    The 'mfa_verified' claim must be present in the JWT access token.
    """

    message = "MFA verification required."

    def has_permission(self, request, view):
        # 1. Basic auth check (should be handled by IsAuthenticated, but let's be explicit)
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Check if MFA is enabled for this user
        # We use hasattr because mfa_settings is a OneToOneField which might not exist
        if hasattr(request.user, "mfa_settings") and request.user.mfa_settings.enabled:
            # 3. If MFA is enabled, the token MUST have the mfa_verified claim
            # request.auth is the validated token object in rest_framework_simplejwt
            if not request.auth:
                return False

            return request.auth.get("mfa_verified", False)

        # 4. If MFA is not enabled, user is allowed (soft policy)
        return True
