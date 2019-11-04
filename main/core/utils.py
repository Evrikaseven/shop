import hashlib
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def get_file_hash(file_field):
    hash_method = hashlib.sha256()
    for line in file_field.open(mode='rb'):
        hash_method.update(line)
    return hash_method.hexdigest()


def shop_send_email(template: str, context: dict, subject: str, to: list, cc: list=None, bcc: list=None):
    if not cc:
        cc = []
    if not bcc:
        bcc = []
    html_message = render_to_string(template, context)
    em = EmailMessage(subject=subject, body=html_message, from_email=settings.EMAIL_HOST_USER, to=to, cc=cc, bcc=bcc)
    em.content_subtype = 'html'
    em.send()
