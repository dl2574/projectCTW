from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from django import forms
from django.forms import ModelForm

from allauth.account.forms import (
    AddEmailForm,
    ChangePasswordForm,
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SignupForm,
)

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
                    "class": "form-checkbox h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
                })
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.update({
                    "class": "form-file cursor-pointer",
                })
            else:
                field.widget.attrs.update({
                    "class": "form-input"
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
            "class": "form-input",
            "placeholder": ""
        })
        self.fields["password"].widget.attrs.update({
            "class": "form-input",
            "placeholder": ""
        })
        self.fields["remember"].widget.attrs.update({
            "class": "form-checkbox h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-600"
        })


class CustomAddEmailForm(AddEmailForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({
            "class": "form-input",
            "placeholder": ""
        })


class CustomChangePasswordForm(ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})


class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({
            "class": "form-input",
            "placeholder": ""
        })


class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})


class CustomSignupForm(SignupForm):
    captcha = hCaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs.update({
            "class": "form-input",
            "placeholder": ""
        })
        self.fields["password1"].widget.attrs.update({
            "class": "form-input",
            "placeholder": ""
        })
