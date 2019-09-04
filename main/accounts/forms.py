from django.contrib.auth.forms import UserCreationForm
from django import forms
from main.models import User


class UserSignUpForm(UserCreationForm):
    phone = forms.CharField(label='Телефон', max_length=20, required=True)
    location = forms.CharField(label='Адрес доставки', max_length=255, required=True)
    birth_date = forms.DateField(label='Дата рождения', required=True, input_formats=['%d/%m/%Y',
                                                                                      '%d %m %Y',
                                                                                      '%d.%m.%Y',
                                                                                      '%d-%m-%Y'])

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'password1', 'password2', 'first_name',
                  'last_name', 'phone', 'birth_date', 'location')
