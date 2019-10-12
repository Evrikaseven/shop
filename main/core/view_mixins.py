from django.contrib.auth.mixins import AccessMixin
from django.conf import settings
from main.core.constants import Roles, OrderStatuses, SHOP_TITLE
from main.models import User, Order, OrderItem


class LoginRolesRequiredViewMixin(AccessMixin):
    """
    Verify that the current user is authenticated and has allowed role
    required_roles class attribute should be provided to add roles
    required_roles = () by default - no one role is allowed except ADMINISTRATOR
    Example:
        allowed_roles = (Roles.ZAKAZSCHIK, Roles.ZAKUPSCHIK) - access is allowed for
        ZAKAZSCHIK, ZAKUPSCHIK, ADMINISTRATOR
    """

    allowed_roles = ()

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


class LoginRolesOwnerRequiredUpdateViewMixin(LoginRolesRequiredViewMixin):
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
    allowed_non_owner_roles = ()

    def _is_it_allowed(self, **kwargs) -> bool:
        pk = kwargs.get('pk') or kwargs.get('id')
        allowed_non_owner_roles = set(self.allowed_non_owner_roles) | {Roles.ADMINISTRATOR}

        if self.model is User:
            if self.user != self.model.objects.get(pk=pk) and self.user.role not in allowed_non_owner_roles:
                return False
        elif self.model is not None:
            instance = self.model.objects.get(pk=pk)
            if getattr(instance, 'created_by', None) != self.user and self.user.role not in allowed_non_owner_roles:
                return False
        elif hasattr(self, 'order_id') and self.order_id:
            order = Order.objects.get(pk=self.order_id)
            user = order.created_by
            if user != self.user and self.user.role not in allowed_non_owner_roles:
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


class OrderCreateStatusOnlyAllowUpdateViewMixin(LoginRolesOwnerRequiredUpdateViewMixin):
    roles_allowed_to_update_order_in_create_status_only = (Roles.ZAKAZSCHIK,)

    def _is_it_allowed_to_update_order(self, **kwargs):
        pk = kwargs.get('pk') or kwargs.get('id')
        order = None

        if self.model is Order:
            order = self.model.objects.get(pk=pk)
        elif self.model is OrderItem:
            if hasattr(self, 'order_id') and self.order_id:
                order = Order.objects.get(pk=self.order_id)
            else:
                order = self.model.objects.get(pk=pk).order
        elif getattr(self, 'order_item', None):
            order_item = getattr(self, 'order_item', None)
            order = order_item.order

        if (order and order.status != OrderStatuses.CREATED and
                self.user.role in self.roles_allowed_to_update_order_in_create_status_only):
            return False
        return super()._is_it_allowed(**kwargs)

    def post(self, *args, **kwargs):
        if not self._is_it_allowed_to_update_order(**kwargs):
            return self.handle_no_permission()
        return super().post(*args, **kwargs)


class CommonContextViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shop_title'] = SHOP_TITLE
        if self.user.is_authenticated:
            context['user_pk'] = self.user.pk
            context['email'] = self.user.email
            context['user_role'] = self.user.role
            context['roles'] = Roles
            context['user_is_authenticated'] = True
            context['user_first_name'] = self.user.first_name
            context['user_last_name'] = self.user.last_name
            context['MEDIA_URL'] = settings.MEDIA_URL
        return context

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        return super().dispatch(request, *args, **kwargs)
