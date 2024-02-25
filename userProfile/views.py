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
    # success_url = 
    
    # def get_absolute_url(self):
    #     return reverse("userProfile/user_profile.html", kwargs={"username":self.username})
    
    def test_func(self) -> bool | None:
        obj = self.get_object()
        return obj.id == self.request.user.id
    
account_profile = AccountProfileView.as_view()