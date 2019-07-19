from django.contrib.auth.mixins import AccessMixin
from main.models import Roles


class LoginRolesRequiredMixin(AccessMixin):
    """
    Verify that the current user is authenticated and has allowed role
    required_roles class attribute should be provided to add roles
    required_roles = () by default - no one role is allowed except ADMINISTRATOR
    Example:
        required_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK) - access is allowed for
        ZAKAZSCHIK, ZAKUPSCHIK, ADMINISTRATOR
    """

    required_roles = ()

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()
        if user.role not in self.required_roles and user.role != Roles.ADMINISTRATOR:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
