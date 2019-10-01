from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django import forms
from django.core.exceptions import ValidationError
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


class CustomPasswordResetForm(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).count():
            raise ValidationError('Пользователь с {email} не найдет, проверьте, пожалуйста, введенный email'
                                  .format(email=email))
        return email
