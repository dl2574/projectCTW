from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from django import forms
from django.forms import ModelForm

from allauth.account.forms import LoginForm, SignupForm

from hcaptcha.fields import hCaptchaField

CustomUser = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "username",
        )


class CustomUserChangeForm(ModelForm):
    MAX_PROFILE_PICTURE_SIZE = 2 * 1024 * 1024

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "first_name",
            "last_name",
            "bio",
            "email_status_updates",
            "email_event_reminders",
            "profile_picture",
        )
        widgets = {
            "profile_picture": forms.FileInput,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply different styling to checkboxes vs text inputs — the ring/shadow
        # style for text inputs looks wrong on a native checkbox element.
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({
                    "class": "h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
                })
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({
                    "class": "cursor-pointer",
                })
            else:
                field.widget.attrs.update({
                    "class": "block w-full rounded-md border-0 p-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
                })

    def clean_profile_picture(self):
        file = self.cleaned_data.get("profile_picture")

        if file:
            if file.size > self.MAX_PROFILE_PICTURE_SIZE:
                raise ValidationError(f"File size must be under {
                                      self.MAX_PROFILE_PICTURE_SIZE / (1024 * 1024):.2f} MB.")

        return file


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["login"].widget.attrs.update({
            "class": "block w-full rounded-md border-0 py-1.5 px-1 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6",
            "placeholder": ""
        })
        self.fields["password"].widget.attrs.update({
            "class": "block w-full rounded-md border-0 py-1.5 px-1 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6",
            "placeholder": ""
        })
        self.fields["remember"].widget.attrs.update({
            "class": "h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
        })


class CustomSignupForm(SignupForm):
    captcha = hCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({
            "class": "block w-full rounded-md border-0 py-1.5 px-1 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6",
            "placeholder": ""
        })
        self.fields["password1"].widget.attrs.update({
            "class": "block w-full rounded-md border-0 py-1.5 px-1 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6",
            "placeholder": ""
        })
