from django import forms
from .models import *


class ProviderForm(forms.ModelForm):

    class Meta:
        model = Provider
        exclude = [""]
