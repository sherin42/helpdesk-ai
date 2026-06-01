from django.core.management.base import BaseCommand

from django.utils import timezone

from datetime import timedelta

from tickets.models import Ticket, TicketHistory


class Command(BaseCommand):

    help = 'Automatically escalate delayed tickets'


    def handle(self, *args, **kwargs):

        now = timezone.now()

        escalated_count = 0

        # =========================
        # GET OPEN TICKETS ONLY
        # =========================

        tickets = Ticket.objects.filter(
            status='open'
        )

        for ticket in tickets:

            # TIME DIFFERENCE
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
            # ESCALATE
            # =========================

            if should_escalate:

                ticket.status = 'escalated'

                ticket.escalation_reason = (
                    'Automatically escalated due to delay'
                )

                ticket.save()

                # HISTORY
                TicketHistory.objects.create(

                    ticket=ticket,

                    action='Automatically escalated by system',

                    performed_by=None

                )

                escalated_count += 1


        self.stdout.write(

            self.style.SUCCESS(

                f'{escalated_count} tickets escalated successfully.'

            )

        )