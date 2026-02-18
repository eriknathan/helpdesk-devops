from django.core.management.base import BaseCommand

from app_teams.models import Team
from app_tickets.models import AuditLog, Ticket
from app_tickets.sla import is_rt_breached


class Command(BaseCommand):
    help = 'Verifica chamados com SLA de RT estourado e escalona para N2.'

    def handle(self, *args, **options):
        active_statuses = [
            Ticket.Status.TRIAGE,
            Ticket.Status.IN_PROGRESS,
            Ticket.Status.WAITING_CUSTOMER,
        ]
        tickets = Ticket.objects.filter(
            status__in=active_statuses,
            is_escalated=False,
        ).select_related('assigned_team')

        escalated = 0
        for ticket in tickets:
            if is_rt_breached(ticket):
                self._escalate(ticket)
                escalated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'{escalated} chamado(s) escalonado(s).'
            )
        )

    def _escalate(self, ticket):
        from django.utils import timezone

        n2_team = Team.objects.filter(
            level=Team.Level.N2,
        ).first()

        ticket.rt_breached_at = timezone.now()
        ticket.is_escalated = True
        if n2_team:
            ticket.assigned_team = n2_team
        ticket.save(update_fields=[
            'rt_breached_at',
            'is_escalated',
            'assigned_team',
        ])

        AuditLog.objects.create(
            ticket=ticket,
            changed_by=None,
            changed_by_name='SYSTEM',
            old_status=ticket.status,
            new_status=ticket.status,
            reason='RT_BREACHED_ESCALATED — SLA estourado, '
                   'escalonado para N2.',
        )
