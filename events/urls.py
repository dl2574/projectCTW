from django.urls import path
from . import views

urlpatterns = [
    path("", views.proposedEvents, name="proposals"),
    path("create/", views.createEvent, name="createEvent"),
    path("edit/<int:pk>", views.editEvent, name="editEvent"),
    path("upvote/<str:pk>", views.upvoteEvent, name="upvote"),
]
