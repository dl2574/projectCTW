from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = [
        "email",
        "username",
        "is_staff",
    ]

admin.site.register(User, CustomUserAdmin)
