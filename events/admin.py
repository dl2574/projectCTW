from django.contrib import admin
from .models import Event, Plan, ProposedDate

admin.site.register(Event)
admin.site.register(Plan)
admin.site.register(ProposedDate)
