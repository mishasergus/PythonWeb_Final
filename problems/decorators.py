from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from Shared_models.models import CustomUser

def staff_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role not in [CustomUser.Role.AGENT, CustomUser.Role.MANAGER]:
            raise PermissionDenied("Доступ дозволено лише агентам та менеджерам")
        return view_func(request, *args, **kwargs)
    return wrapper

def manager_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != CustomUser.Role.MANAGER and not request.user.is_superuser:
            raise PermissionDenied("Доступ дозволено лише менеджерам")
        return view_func(request, *args, **kwargs)
    return wrapper

def client_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != CustomUser.Role.CLIENT:
            raise PermissionDenied("Доступ дозволено лише клієнтам")
        return view_func(request, *args, **kwargs)
    return wrapper