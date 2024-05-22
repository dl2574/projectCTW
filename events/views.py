from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DetailView, ListView

from .forms import EventForm
from .models import Event
from django.contrib.auth.decorators import login_required



class ProposedEvents(ListView):
    model = Event
    template_name = "events/proposed_events.html"
    context_object_name = "events"
    
proposedEvents = ProposedEvents.as_view()


@login_required(login_url="account_login")
def createEvent(request):
    form = EventForm()

    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            return redirect("proposals")

    context = {"form": form}
    return render(request, "events/create_event.html", context)


@login_required(login_url="account_login")
def editEvent(request, pk):
    event = Event.objects.get(id=pk)
    if request.user != event.created_by:
        return redirect("home")

    form = EventForm(instance=event)

    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")

    context = {"form": form}
    return render(request, "events/create_event.html", context)

class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"

    
detailView = EventDetailView.as_view()


@login_required(login_url="account_login")
def upvoteEvent(request, pk):
    user = request.user
    event = get_object_or_404(Event, id=pk)
    thumb = "fa-regular"

    if event.user_upvoted(user):
        event.upvotes.remove(user)
    else:
        event.upvotes.add(user)
        thumb = "fa-solid"

    num_of_votes = event.number_of_upvotes()
    vote_text = "Vote" if num_of_votes == 1 else "Votes"
    
    responseString = f"<html><i class='{thumb} fa-thumbs-up'></i> {num_of_votes} Up {vote_text}<html>"
    return HttpResponse(responseString)
