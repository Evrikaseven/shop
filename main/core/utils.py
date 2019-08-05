from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from main.models import User
from main.core.constants import Roles


def send_new_order_created_email(user, order):
    context = {
        'user': user,
        'order': order,
    }
    s = render_to_string('main/email_order_paying.html', context)
    admins = User.objects.filter(role=Roles.ADMINISTRATOR)
    conn = get_connection()
    conn.open()
    em = EmailMessage(subject='Новый заказ оплачен', body=s, to=[admin.email for admin in admins], connection=conn)
    em.send()
    conn.close()
