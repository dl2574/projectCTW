from django.forms import ModelForm
from .models import Event, Comment


class EventForm(ModelForm):
    class Meta():
        model = Event
        fields = ['name', 'description', 'location']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})


class CommentForm(ModelForm):
    class Meta():
        model = Comment
        fields = ['comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-input"})
