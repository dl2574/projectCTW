from django.shortcuts import render, redirect
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

    context = {'form': form}
    return render(request, 'events/create_event.html', context)