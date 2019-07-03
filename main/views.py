from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth import views as auth_views
from .forms import ProviderForm, UserSignUpForm
from .models import Provider


# Create your views here.
# def index(request):
#
#     # form = ProviderForm(request.POST or None)
#     # context = dict(form=form, providers=None)
#     # if request.method == "POST" and form.is_valid():
#     #     form.save()
#
#     if request.method == 'GET':
#         context['providers'] = Provider.objects.all()
#
#     return render(request, 'main/index.html', context)


class IndexView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = Provider.objects.all()
        return context


class UserSignUpView(CreateView):
    template_name = 'main/signup.html'
    form_class = UserSignUpForm
    success_url = '/signup/done/'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        return context


class SignUpDoneView(TemplateView):
    template_name = 'main/signup_done.html'
