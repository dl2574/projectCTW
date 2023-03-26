from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import EventForm
from .models import Event
from django.contrib.auth.decorators import login_required


def proposedEvents(request):
    events = Event.objects.all()
    context = {"events": events}
    return render(request, 'events/proposed_events.html', context)


@login_required(login_url="login")
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


@login_required(login_url="login")
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


@login_required()
def upvoteEvent(request, pk):
    user = request.user
    event = get_object_or_404(Event, id=pk)

    if event.upvotes.filter(id=user.id).exists():
        event.upvotes.remove(user)
    else:
        event.upvotes.add(user)

    responseString = f"{event.number_of_upvotes()} Up Votes"
    return HttpResponse(responseString)
