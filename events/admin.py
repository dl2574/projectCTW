from django.contrib import admin
from .models import Event, Plan, ProposedDate, Comment

admin.site.register(Event)
admin.site.register(Plan)
admin.site.register(ProposedDate)
admin.site.register(Comment)
