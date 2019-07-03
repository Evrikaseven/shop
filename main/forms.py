from django import forms
from .models import Provider, User
from django.contrib.auth.forms import UserCreationForm


class ProviderForm(forms.ModelForm):
    name = forms.CharField(label='Имя', help_text='Имя поставщика')
    vk_link = forms.CharField(label='Ссылка Вконтакте', help_text='URL профиля Вконтакте')
    space = forms.CharField(label='Место', help_text='Номер места поставщика')
    description = forms.CharField(label='Описание', widget=forms.Textarea, help_text='Описание с данными поставщика')
    picture = forms.CharField(label='Изображение', help_text='URL либо путь к картинке')
    product_type = forms.CharField(label='Чем торгует', help_text='Вид товара')

    class Meta:
        model = Provider
        exclude = []


class UserSignUpForm(UserCreationForm):
    username = forms.CharField(label='Логин', required=True)
    phone = forms.CharField(label='Телефон', max_length=20, required=True)
    location = forms.CharField(label='Адрес', max_length=255, required=True)
    birth_date = forms.DateField(label='Дата рождения', required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'first_name',
                  'last_name', 'email', 'phone', 'birth_date', 'location')

