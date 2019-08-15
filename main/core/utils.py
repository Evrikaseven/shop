from django.core.mail import EmailMessage, get_connection, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from main.models import User
from main.core.constants import Roles


def shop_send_email(template: str, context: dict, subject: str, to: list):
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)
    admins = [admin.email for admin in User.objects.filter(role=Roles.ADMINISTRATOR)]
    recipient_list = to + admins
    send_mail(subject, plain_message,
              settings.EMAIL_HOST_USER,
              recipient_list,
              fail_silently=False,
              auth_user=None,
              auth_password=None,
              connection=None,
              html_message=html_message)


def send_user_updates_email(email_context: dict, email_subject: str, email_to: list):
    email_template = 'main/email_user_changes.html'
    email_context = {
        'user': user,
    }
    email_to = [user.email]
    shop_send_email(email_template, email_context, email_subject, email_to)
