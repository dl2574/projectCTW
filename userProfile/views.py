from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from .models import User

def loginUser(request):
    page = "login"

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

    context = {"page": page}
    return render(request, 'userProfile/login_register.html', context)

def registerUser(request):
    page = "register"
    form = CustomUserCreationForm()

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            login(request, user)
            return redirect("home")
    
    context = {"form": form, "page": page}
    return render(request, "userProfile/login_register.html", context)

def logoutUser(request):
    logout(request)
    return redirect("login")

def userProfile(request, pk):
    profile = get_object_or_404(User, id=pk)

    context = {"profile": profile}
    return render(request, "userProfile/user_profile.html", context)

