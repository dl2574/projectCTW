from django.urls import path
from . import views

urlpatterns = [
    path("", views.proposedEvents, name="proposals"),
    path("create/", views.createEvent, name="createEvent"),
    path("detail/<uuid:pk>/", views.detailView, name="eventDetail"),
    path("detail/plan/<uuid:pk>/", views.planView, name="eventPlan"),
    path("edit/<uuid:pk>/", views.editEvent, name="editEvent"),
    path("upvote/<str:pk>/", views.upvoteEvent, name="upvote"),
]
