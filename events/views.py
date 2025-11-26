from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DetailView, ListView

from .forms import EventForm, CommentForm
from .models import Event, Comment
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

    context = {"form": form, "method": "create"}
    return render(request, "events/event_form.html", context)


@login_required(login_url="account_login")
def editEvent(request, pk):
    event = get_object_or_404(Event, id=pk)

    # Check if the logged-in user is the creator of the event
    if request.user != event.created_by:
        return redirect(event) # Redirect to the event detail page (or some other page)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save() # Update the event object in the database
            # Redirect to the event's detail page after saving
            return redirect("eventDetail", pk=event.id)
    else:
        form = EventForm(instance=event)

    context = {"form": form, "method": "edit", "pk": pk}
    return render(request, "events/event_form.html", context)



def detailView(request, pk):
    event = get_object_or_404(Event, id=pk)
    event_comments = event.comment_set.all()

    if request.method == "POST":
        if request.user.is_authenticated:
            form = CommentForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.event = event
                comment.created_by = request.user
                comment.save()
                return redirect(event)
            else:
                event_comments = event.comment_set.all()
                context = {
                    "comments": event_comments,
                    "commentForm": form,
                    "event": event
                }
                return render(request, "events/event_detail.html", context)
        else:
            return redirect("account_login")

    context = {"comments": event_comments, "commentForm": CommentForm, "event": event}
    return render(request, "events/event_detail.html", context)


@login_required(login_url="account_login")
def upvoteEvent(request, pk):
    user = request.user
    event = get_object_or_404(Event, id=pk)
    thumb = "fa-regular"

    # Check if the user has upvoted this event already
    if event.user_upvoted(user):
        # If already upvoted, remove upvote
        event.upvotes.remove(user)
    else:
        # Add upvote
        event.upvotes.add(user)
        thumb = "fa-solid"

    num_of_votes = event.number_of_upvotes()

    # Check if this the vote count is above the required number of upvotes. If so, change status to planning.
    if num_of_votes > event.required_num_upvotes:
        event.status = Event.StatusCode.PLANNING
        event.save()

    vote_text = "Vote" if num_of_votes == 1 else "Votes"
    
    responseString = f"<html><i class='{thumb} fa-thumbs-up'></i> {num_of_votes} Up {vote_text}<html>"
    return HttpResponse(responseString)


