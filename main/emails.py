
from main.models import User, Order
from main.core.constants import Roles, OrderStatuses
from main.core.utils import shop_send_email


def user_data_email(user: User, subject: str, extra_params: dict):
    email_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'email': user.email,
        'delivery_address': user.delivery_address,
        'birth_date': user.birth_date,
        'role': Roles[user.role],
        'balance': user.balance,
        'balance_changed': False,
    }
    email_data.update(extra_params)
    admins = [admin.email for admin in User.objects.get_list(role=Roles.ADMINISTRATOR)]
    shop_send_email(template='main/email_user_template.html',
                    context=email_data,
                    subject=subject,
                    to=[user.email],
                    bcc=[admins])


def order_data_email(order: Order, subject: str, extra_params: dict):
    user = order.created_by
    email_data = {
        'order_pk': order.pk,
        'order_price': order.price,
        'email': user.email,
        'status': OrderStatuses[order.status],
        'paid_price': order.paid_price,
        'status_changed': False,
        'paid_price_changed': False,
    }
    email_data.update(extra_params)
    admins = [admin.email for admin in User.objects.get_list(role=Roles.ADMINISTRATOR)]
    shop_send_email(template='main/email_order_template.html',
                    context=email_data,
                    subject=subject,
                    to=[user.email],
                    bcc=[admins])
