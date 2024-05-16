from django.db import models

from django.contrib.auth import get_user_model

from ..events.models import Event

User = get_user_model()

class Notification(models.Model):
    message = models.CharField(max_length=150, blank=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_created=True)
    read = models.BooleanField(default=False)
    
    def mark_read(self):
        self.read = True
        
    
class EventStatusChange(Notification):
    source_event = models.ForeignKey(Event, on_delete=models.CASCADE)
    

class FriendRequest(Notification):
    originator = models.ForeignKey(User, on_delete=models.CASCADE)