from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Ticket(models.Model):

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
        ('escalated', 'Escalated'),
        ('external', 'External'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tickets')
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    assigned_to = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('open', 'Open'),
            ('in_progress', 'In Progress'),
            ('resolved', 'Resolved'),
            ('escalated', 'Escalated')
        ],
        default='open'
    )

    escalation_reason = models.TextField(blank=True, null=True)

    last_assigned_at = models.DateTimeField(
        null=True,
        blank=True
    )


class Comment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class TicketHistory(models.Model):

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='history'
    )

    action = models.CharField(max_length=255)

    performed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.action
