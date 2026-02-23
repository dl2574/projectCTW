from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView

from django.urls import reverse

from django.contrib.auth import get_user_model

from .forms import CustomUserChangeForm


class UserProfileView(DetailView):
    model = get_user_model()
    template_name = "userProfile/user_profile.html"
    login_url = "account_login"
    slug_field = "username"
    
user_profile = UserProfileView.as_view()


class AccountProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = get_user_model()
    template_name = "userProfile/user_account.html"
    login_url = "account_login"
    slug_field = "username"
    form_class = CustomUserChangeForm

    def test_func(self):
        # Users may only edit their own account settings, not anyone else's.
        return self.request.user == self.get_object()

    def get_success_url(self):
        return reverse("account_profile", kwargs={"slug": self.object.username})


account_profile = AccountProfileView.as_view()