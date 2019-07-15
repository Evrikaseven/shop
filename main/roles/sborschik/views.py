from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class SborschikMainView(LoginRequiredMixin, TemplateView):
    template_name = 'main/sborschik.html'
    url_name = 'sborschik'
