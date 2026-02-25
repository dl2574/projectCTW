from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DetailView, ListView

from .forms import EventForm, CommentForm
from .models import Event, Comment, Plan
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
        # Redirect to the event detail page (or some other page)
        return redirect(event)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()  # Update the event object in the database
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

    context = {"comments": event_comments,
               "commentForm": CommentForm, "event": event}
    return render(request, "events/event_detail.html", context)


@login_required(login_url="account_login")
def upvoteEvent(request, pk):
    user = request.user
    event = get_object_or_404(Event, id=pk)

    if event.user_upvoted(user):
        event.upvotes.remove(user)
    else:
        event.upvotes.add(user)
        # Only attempt transition on new upvotes (not removals)
        if event.number_of_upvotes() >= event.required_num_upvotes and event.status == event.StatusCode.PROPOSAL:
            event.transition_to_planning()

    user_upvoted = event.user_upvoted(user)
    context = {'event': event, 'user_upvoted': user_upvoted}

    # Return the appropriate partial based on which element htmx is targeting
    hx_target = request.headers.get('HX-Target', '')
    if hx_target == 'event-header':
        primary = render(request, 'events/event_detail.html#event-header', context)
        # Render the sidebar count as a second fragment and mark it for OOB swap
        # so HTMX updates both disconnected elements from a single response.
        oob_html = render_to_string(
            'events/event_detail.html#sidebar-upvote-count', context, request=request
        )
        oob_html = oob_html.replace(
            'id="sidebar-upvote-count"',
            'id="sidebar-upvote-count" hx-swap-oob="outerHTML"',
            1,
        )
        primary.content += oob_html.encode()
        return primary
    return render(request, 'events/proposed_events.html#event-card', context)
