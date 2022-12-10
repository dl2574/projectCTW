from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()