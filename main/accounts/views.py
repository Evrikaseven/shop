from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import UserSignUpForm


class UserSignUpView(CreateView):
    template_name = 'main/signup.html'
    form_class = UserSignUpForm
    success_url = reverse_lazy('main:signup_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context


class SignUpDoneView(TemplateView):
    template_name = 'main/signup_done.html'
