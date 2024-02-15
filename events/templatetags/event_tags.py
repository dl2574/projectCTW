from django import template
from ..models import Event



register = template.Library()

@register.filter
def upvoted(event, user):
    """
        Used in an if statement and returns a bool indicating if a user upvoted the filtered event.
        
        Utilizes the Event model method user_upvoted
    """
    return event.user_upvoted(user)

# register.filter("upvoted", upvoted)

@register.simple_tag
def event_status(status):
    color = "yellow"
    if status == "PL":
        color = "purple"
    elif status == "SC":
        color = "blue"
    elif status == "CO":
        color = "green"
    elif status == "AR":
        color = "gray"
    elif status == "DN":
        color = "red"
    elif status == "RM":
        color = "red"
    return f"text-{color}-400"