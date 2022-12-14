from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from .models import User
from django.utils.translation import gettext_lazy as _


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name'
        }
        help_texts = {
            'username': None,
            'password1': None,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()