import hashlib
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from threading import Thread


def get_file_hash(file_field):
    hash_method = hashlib.sha256()
    for line in file_field.open(mode='rb'):
        hash_method.update(line)
    return hash_method.hexdigest()


class SendEmailThread(Thread):

    def __init__(self, template: str, context: dict, subject: str, to: list, cc: list = None, bcc: list = None):
        self.template = template
        self.context = context
        self.subject = subject
        self.to = to
        self.cc = cc if cc else []
        self.bcc = bcc if bcc else []
        super().__init__()

    def run(self):
        html_message = render_to_string(self.template, self.context)
        em = EmailMessage(subject=self.subject,
                          body=html_message,
                          from_email=settings.EMAIL_HOST_USER,
                          to=self.to,
                          cc=self.cc,
                          bcc=self.bcc)
        em.content_subtype = 'html'
        em.send()


def shop_send_email(template: str, context: dict, subject: str, to: list, cc: list = None, bcc: list = None):
    send_email_thread = SendEmailThread(template, context, subject, to, cc, bcc)
    send_email_thread.start()
