from django.contrib.auth.mixins import AccessMixin
from main.models import Roles
from main.models import User


class LoginRolesRequiredMixin(AccessMixin):
    """
    Verify that the current user is authenticated and has allowed role
    required_roles class attribute should be provided to add roles
    required_roles = () by default - no one role is allowed except ADMINISTRATOR
    Example:
        allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK) - access is allowed for
        ZAKAZSCHIK, ZAKUPSCHIK, ADMINISTRATOR
    """

    allowed_roles = set()

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        if not self.user.is_authenticated:
            return self.handle_no_permission()
        if self.user.role not in self.allowed_roles and self.user.role != Roles.ADMINISTRATOR:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class LoginRolesOwnerRequiredUpdateViewMixin(LoginRolesRequiredMixin):
    """
        Verify that the current user is authenticated and has allowed role
        required_roles class attribute should be provided to add roles
        required_roles = () by default - no one role is allowed except ADMINISTRATOR
        Also it allows updating instance for not owners with roles in allowed_non_owner_roles
        Example:
            allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK) - access is allowed for
            ZAKAZSCHIK, ZAKUPSCHIK, ADMINISTRATOR
            allowed_non_owner_roles = (Roles.ZAKUPSCHIK, ) - will allow update any instances for
            ZAKUPSCHIK and ADMINISTRATOR. For ZAKAZSCHIK other instances updating will be forbidden,
            only its own possible to change
    """
    allowed_non_owner_roles = set()

    def _is_it_allowed(self, **kwargs) -> bool:
        pk = kwargs.get('pk') or kwargs.get('id')
        allowed_non_owner_roles = set(self.allowed_non_owner_roles) | {Roles.ADMINISTRATOR}

        if self.model is User:
            if self.user != self.model.objects.get(pk=pk) and self.user.role not in allowed_non_owner_roles:
                return False
        else:
            instance = self.model.objects.get(pk=pk)
            if getattr(instance, 'created_by', None) != self.user and self.user.role not in allowed_non_owner_roles:
                return False
        return True

    def get(self, *args, **kwargs):
        if not self._is_it_allowed(**kwargs):
            return self.handle_no_permission()
        return super().get(*args, **kwargs)

    def post(self, *args, **kwargs):
        if not self._is_it_allowed(**kwargs):
            return self.handle_no_permission()
        return super().post(*args, **kwargs)


class WithRolesInContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self.user, 'role'):
            context['user_role'] = self.user.role
            context['roles'] = Roles
        return context
