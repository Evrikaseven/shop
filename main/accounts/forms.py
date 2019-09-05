from django.contrib.auth.forms import UserCreationForm
from django import forms
from main.models import User


class UserSignUpForm(UserCreationForm):
    phone = forms.CharField(label='Телефон', max_length=20, required=True)
    delivery_address = forms.CharField(label='Адрес доставки', max_length=255, required=True)
    birth_date = forms.DateField(label='Дата рождения', required=True, input_formats=['%Y-%m-%d'])

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'password1', 'password2', 'first_name',
                  'last_name', 'phone', 'birth_date', 'delivery_address')

    def __init__(self, *args, **kwargs):
        saved_values = kwargs.pop('saved_values', {})
        super().__init__(*args, **kwargs)
        for field in saved_values:
            if field in self.fields:
                self.fields[field].initial = saved_values[field]

