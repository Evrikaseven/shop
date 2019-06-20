from django.shortcuts import render
from .forms import ProviderForm


# Create your views here.
def index(request):

    form = ProviderForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form = form.save()

    return render(request, 'main/index.html', locals())
