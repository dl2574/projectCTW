from django.urls import path
from . import views

urlpatterns = [
    path("", views.proposedEvents, name="proposals"),
    path("create/", views.createEvent, name="createEvent"),
    path("detail/<uuid:pk>/", views.detailView, name="eventDetail"),
    path("edit/<uuid:pk>/", views.editEvent, name="editEvent"),
    path("upvote/<str:pk>/", views.upvoteEvent, name="upvote"),
    path("createComment<str:pk>/", views.createComment, name="createComment"),
]
