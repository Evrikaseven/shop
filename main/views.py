from django.shortcuts import render
from .forms import ProviderForm
from .models import Provider


# Create your views here.
def index(request):

    form = ProviderForm(request.POST or None)
    context = dict(form=form, providers=None)
    if request.method == "POST" and form.is_valid():
        form.save()

    if request.method == 'GET':
        context['providers'] = Provider.objects.all()

    return render(request, 'main/index.html', context)
