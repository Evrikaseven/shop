from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy
from .forms import UserSignUpForm, CustomPasswordResetForm
from main.models import User
from main.emails import user_data_email
from main.core.view_mixins import CommonContextViewMixin
from main.core.constants import SHOP_TITLE


class UserSignUpView(CommonContextViewMixin, CreateView):
    template_name = 'main/account_signup.html'
    form_class = UserSignUpForm

    def __init__(self, *args, **kwargs):
        self.post_fields_data = {}
        super().__init__(*args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('main:signup_done', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        fields = self.form_class._meta.fields   # pylint: disable=no-member
        kwargs['saved_values'] = {
            field: self.post_fields_data[field] for field in fields if field in self.post_fields_data
        }
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        self.post_fields_data = request.POST
        return super().dispatch(request, *args, **kwargs)


class SignUpDoneView(CommonContextViewMixin, TemplateView):
    template_name = 'main/account_signup_done.html'

    def dispatch(self, *args, **kwargs):
        user_pk = kwargs['pk']
        user = User.objects.get(pk=user_pk)
        user_data_email(user=user, subject='Добавлен новый пользователь', extra_params={})
        return super().dispatch(*args, **kwargs)


class CustomPasswordChangeView(CommonContextViewMixin, PasswordChangeView):
    template_name = 'main/account_password_change.html'
    success_url = reverse_lazy('main:password_change_done')


class CustomPasswordChangeDoneView(CommonContextViewMixin, PasswordChangeDoneView):
    template_name = 'main/account_password_change_done.html'


class CustomPasswordResetView(CommonContextViewMixin, PasswordResetView):
    template_name = 'main/account_password_reset.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('main:password_reset_done')
    subject_template_name = 'main/account_password_reset_subject.txt'
    email_template_name = 'main/account_password_reset_email.html'
    html_email_template_name = 'main/account_password_reset_email.html'
    extra_email_context = {'shop_title': SHOP_TITLE}


class CustomPasswordResetDoneView(CommonContextViewMixin, PasswordResetDoneView):
    template_name = 'main/account_password_reset_done.html'


class CustomPasswordResetConfirmView(CommonContextViewMixin, PasswordResetConfirmView):
    template_name = 'main/account_password_reset_confirm.html'
    post_reset_login = True
    success_url = reverse_lazy('main:password_reset_complete')


class CustomPasswordResetCompleteView(CommonContextViewMixin, PasswordResetCompleteView):
    template_name = 'main/account_password_change_done.html'
