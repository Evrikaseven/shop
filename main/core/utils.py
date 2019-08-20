from django.core.mail import EmailMessage, get_connection, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from main.models import User, Order
from main.core.constants import Roles, OrderStatuses


def shop_send_email(template: str, context: dict, subject: str, to: list):
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)
    admins = [admin.email for admin in User.objects.get_list(role=Roles.ADMINISTRATOR)]
    recipient_list = to + admins
    send_mail(subject, plain_message,
              settings.EMAIL_HOST_USER,
              recipient_list,
              fail_silently=False,
              auth_user=None,
              auth_password=None,
              connection=None,
              html_message=html_message)


def user_data_email(user: User, subject: str, extra_params: dict):
    email_data = {
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone': user.phone,
        'email': user.email,
        'location': user.location,
        'birth_date': user.birth_date,
        'role': Roles[user.role],
        'balance': user.balance,
        'balance_changed': False,
    }
    email_data.update(extra_params)
    shop_send_email(template='main/email_user_template.html',
                    context=email_data,
                    subject=subject,
                    to=[user.email])


def order_data_email(order: Order, subject: str, extra_params: dict):
    user = order.created_by
    email_data = {
        'order_pk': order.pk,
        'order_price': order.price,
        'username': user.username,
        'status': OrderStatuses[order.status],
        'paid_price': order.paid_price,
        'status_changed': False,
        'paid_price_changed': False,
    }
    email_data.update(extra_params)
    shop_send_email(template='main/email_order_template.html',
                    context=email_data,
                    subject=subject,
                    to=[user.email])
