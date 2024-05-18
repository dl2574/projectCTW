from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    message = models.CharField(max_length=150, blank=True)
    created_on = models.DateTimeField(auto_created=True)
    read = models.BooleanField(default=False)
    
    def mark_read(self):
        self.read = True
        
    class Meta:
        abstract = True
        
    
class EventStatusChange(Notification):
    source_event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipients")
    

class FriendRequest(Notification):
    originator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="originator")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)