from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

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
