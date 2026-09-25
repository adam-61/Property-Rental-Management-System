from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def owner_required(view_func):
    """Decorator ensuring that only authenticated Property Owners can access the view."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        if not hasattr(request.user, 'profile') or not request.user.profile.is_owner:
            messages.warning(request, "Access restricted: This area is only available to Property Owner accounts.")
            return redirect('property_list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def tenant_required(view_func):
    """Decorator ensuring that only authenticated Tenants can access the view."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")
        if not hasattr(request.user, 'profile') or not request.user.profile.is_tenant:
            messages.warning(request, "Access restricted: This action is intended for Tenant accounts.")
            return redirect('my_properties')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
