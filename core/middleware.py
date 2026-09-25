from django.contrib import messages
from django.shortcuts import redirect


class RoleAccessMiddleware:
    """
    Custom middleware that enforces role-based access control at the request
    layer, as an additional safety net alongside the view-level
    @owner_required / @tenant_required decorators (accounts/decorators.py).

    Any authenticated user whose Profile role does not match the section of
    the site they are trying to reach is redirected -- with a flash message
    -- before the matching view is ever resolved or executed. This means a
    Tenant account can never reach an "/owner/" URL (and vice-versa for the
    tenant-only "my requests" area), even if a view-level check were ever
    missed or a URL were guessed/bookmarked directly.
    """

    # URL path prefixes that only a Property Owner account may access.
    OWNER_ONLY_PREFIXES = ('/owner/',)

    # URL path prefixes that only a Tenant account may access.
    TENANT_ONLY_PREFIXES = ('/requests/', '/tenant/')

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)

            if path.startswith(self.OWNER_ONLY_PREFIXES):
                if not profile or not profile.is_owner:
                    messages.warning(
                        request,
                        "Access restricted: this area is only available to Property Owner accounts."
                    )
                    return redirect('property_list')

            elif any(path.startswith(prefix) for prefix in self.TENANT_ONLY_PREFIXES):
                if not profile or not profile.is_tenant:
                    messages.warning(
                        request,
                        "Access restricted: this area is only available to Tenant accounts."
                    )
                    return redirect('my_properties')

        return self.get_response(request)
