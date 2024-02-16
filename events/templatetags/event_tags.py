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
def event_status_color(status):
    color = "text-yellow-700 border-yellow-500 bg-yellow-100"
    if status == "PL":
        color = "text-purple-700 border-purple-500 bg-purple-100"
    elif status == "SC":
        color = "text-blue-700 border-blue-500 bg-blue-100"
    elif status == "CO":
        color = "text-green-700 border-green-500 bg-green-100"
    elif status == "AR":
        color = "text-gray-700 border-gray-500 bg-gray-100"
    elif status == "DN":
        color = "text-red-700 border-red-500 bg-red-100"
    elif status == "RM":
        color = "text-red-700 border-red-500 bg-red-100"
        
    #return f'<span class="{color} px-3 py-1 rounded-xl border-2">{ event.get_status_display }</span>'
    return color