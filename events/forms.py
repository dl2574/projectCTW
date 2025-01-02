from django.forms import ModelForm
from .models import Event, Comment


class EventForm(ModelForm):
    class Meta():
        model = Event
        fields = ['name', 'description', 'location']

class CommentForm(ModelForm):
    class Meta():
        model = Comment
        fields = ['comment']