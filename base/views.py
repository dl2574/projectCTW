from django.shortcuts import render
from django.contrib import messages


def home(request):
    messages.info(request, "Please excuse our mess. This site is still under construction.")
    return render(request, "base/home.html")


def about(request):
    return render(request, "base/about.html")


def message_test(request):
    messages.info(request, "Test Info")
    messages.success(request, "Test Success")
    messages.warning(request, "Test Warning")
    messages.error(request, "Test Error")
    return render(request, "base/messages.html")