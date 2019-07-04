from django.views.generic.base import TemplateView


class ZakazschikMainView(TemplateView):
    template_name = 'main/zakazschik.html'


class SborschikMainView(TemplateView):
    template_name = 'main/sborschik.html'


class ZakupschikMainView(TemplateView):
    template_name = 'main/zakupschik.html'


class AdministratorMainView(TemplateView):
    template_name = 'main/administrator.html'

