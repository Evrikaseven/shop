from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .forms import UserSignUpForm
from main.models import User
from main.core.utils import user_data_email
from main.core.view_mixins import CommonContextViewMixin


class UserSignUpView(CommonContextViewMixin, CreateView):
    template_name = 'main/signup.html'
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
    template_name = 'main/signup_done.html'

    def dispatch(self, *args, **kwargs):
        user_pk = kwargs['pk']
        user = User.objects.get(pk=user_pk)
        user_data_email(user=user, subject='Добавлен новый пользователь', extra_params={})
        return super().dispatch(*args, **kwargs)
