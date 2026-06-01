from django.contrib import admin

from .models import Ticket, Comment, Department, TicketHistory

# Register your models here.
admin.site.register(Ticket)
admin.site.register(Comment)
admin.site.register(Department)
admin.site.register(TicketHistory)