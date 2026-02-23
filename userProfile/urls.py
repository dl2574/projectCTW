from django.urls import path
from . import views

urlpatterns = [
    path("profile/<str:slug>/", views.user_profile, name="user_profile"),
    path("settings/<str:slug>/", views.account_profile, name="account_profile"),
]
