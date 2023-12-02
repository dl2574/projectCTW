from django.urls import path
from . import views

urlpatterns = [
    # path("login/", views.loginUser, name="login"),
    # path("register/", views.registerUser, name="register"),
    # path("logout/", views.logoutUser, name="logout"),
    path("profile/<str:slug>/", views.user_profile, name="user_profile"),
    path("settings/<str:slug>/", views.account_profile, name="account_profile"),
]
