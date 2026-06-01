from apscheduler.schedulers.background import BackgroundScheduler

from django.utils import timezone

from datetime import timedelta

from .models import Ticket, TicketHistory


def auto_escalate_tickets():

    print("Checking tickets...")

    now = timezone.now()

    tickets = Ticket.objects.filter(
        status__in=['open', 'in_progress']
    )

    for ticket in tickets:

        if ticket.last_assigned_at:

            ticket_age = now - ticket.last_assigned_at

        else:

            ticket_age = now - ticket.created_at

        should_escalate = False

        # =========================
        # HIGH PRIORITY
        # =========================
        if (
            ticket.priority == 'high'
            and ticket_age >= timedelta(hours=24)
        ):

            should_escalate = True

        # =========================
        # MEDIUM PRIORITY
        # =========================
        elif (
            ticket.priority == 'medium'
            and ticket_age >= timedelta(hours=48)
        ):

            should_escalate = True

        # =========================
        # LOW PRIORITY
        # =========================
        elif (
            ticket.priority == 'low'
            and ticket_age >= timedelta(hours=72)
        ):

            should_escalate = True

        # =========================
        # ESCALATE TICKET
        # =========================
        if should_escalate:

            # avoid duplicate escalation
            if ticket.status != 'escalated':

                ticket.status = 'escalated'

                ticket.escalation_reason = (
                    'Automatically escalated due to SLA breach'
                )

                ticket.save()

                TicketHistory.objects.create(

                    ticket=ticket,

                    action=(
                        'Ticket automatically escalated '
                        'due to SLA breach'
                    ),

                    performed_by=None

                )

                print(f"Ticket {ticket.id} escalated")


def start_scheduler():

    scheduler = BackgroundScheduler()

    scheduler.add_job(

        auto_escalate_tickets,

        'interval',

        minutes=1

    )

    scheduler.start()

    print("Scheduler started...")