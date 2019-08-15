from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import UserSignUpForm
from main.models import User
from main.core.utils import shop_send_email
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
        email_data = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone': user.phone,
            'email': user.email,
            'location': user.location,
            'birth_date': user.birth_date,
            'role': Roles[user.role],
        }
        shop_send_email(template='main/email_user_template.html',
                        context=email_data,
                        subject='Добавлен новый пользователь',
                        to=[user.email])
        return super().dispatch(*args, **kwargs)
