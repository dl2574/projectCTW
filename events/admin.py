from django.contrib import admin
from .models import (
    Event, Plan, ProposedDate, Comment,
    SupplyItem, SupplyCommitment, AttendanceCommitment
)

admin.site.register(Event)
admin.site.register(Plan)
admin.site.register(ProposedDate)
admin.site.register(Comment)
admin.site.register(SupplyItem)
admin.site.register(SupplyCommitment)
admin.site.register(AttendanceCommitment)
