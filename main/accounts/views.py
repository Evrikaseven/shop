from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import UserSignUpForm
from main.models import User
from main.core.utils import user_data_email
from main.core.constants import Roles


class UserSignUpView(CreateView):
    template_name = 'main/signup.html'
    form_class = UserSignUpForm

    def get_success_url(self):
        return reverse_lazy('main:signup_done', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context


class SignUpDoneView(TemplateView):
    template_name = 'main/signup_done.html'

    def dispatch(self, *args, **kwargs):
        user_pk = kwargs['pk']
        user = User.objects.get(pk=user_pk)
        user_data_email(user=user, subject='Добавлен новый пользователь', extra_params={})
        return super().dispatch(*args, **kwargs)
