from django.contrib.auth.forms import UserCreationForm
from django import forms
from main.models import User


class UserSignUpForm(UserCreationForm):
    username = forms.CharField(label='Логин', required=True)
    phone = forms.CharField(label='Телефон', max_length=20, required=True)
    location = forms.CharField(label='Адрес', max_length=255, required=True)
    birth_date = forms.DateField(label='Дата рождения', required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'first_name',
                  'last_name', 'email', 'phone', 'birth_date', 'location')
