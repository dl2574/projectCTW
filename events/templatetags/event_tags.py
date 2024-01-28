from django import template



register = template.Library()

@register.filter
def upvoted(event, user):
    """
        Used in an if statement and returns a bool indicating if a user upvoted the filtered event.
        
        Utilizes the Event model method user_upvoted
    """
    return event.user_upvoted(user)

# register.filter("upvoted", upvoted)