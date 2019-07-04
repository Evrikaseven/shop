from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth import views as auth_views
from .forms import ProviderForm
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

    def get(self, request, *args, **kwargs):


        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['providers'] = Provider.objects.all()
        return context




