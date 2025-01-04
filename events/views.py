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

    context = {"form": form}
    return render(request, "events/create_event.html", context)


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

    context = {"form": form}
    return render(request, "events/create_event.html", context)


class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        context["comments"] = self.object.comment_set.all()
        return context

    
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


@login_required(login_url="account_login")
def createComment(request, pk):
    # Get the current user and the event they commented on.
    user = request.user
    event = get_object_or_404(Event, id=pk)

    # Get post information
    userComment = request.comment
    
    # Create comment for the ID'd event
    newCommentObject = Comment.objects.create(comment=userComment, event=event, createdBy=user)
    newCommentObject.save()

    return redirect(event)

