from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic import TemplateView

from app_tickets.models import Ticket


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        qs = Ticket.objects.all()
        if user.is_customer:
            qs = qs.filter(created_by=user)

        ctx['total'] = qs.count()
        ctx['open_count'] = qs.filter(
            status__in=[
                Ticket.Status.OPEN,
                Ticket.Status.TRIAGE,
                Ticket.Status.IN_PROGRESS,
                Ticket.Status.WAITING_CUSTOMER,
            ],
        ).count()
        ctx['resolved_count'] = qs.filter(
            status=Ticket.Status.RESOLVED,
        ).count()
        ctx['closed_count'] = qs.filter(
            status=Ticket.Status.CLOSED,
        ).count()
        ctx['breached_count'] = qs.filter(
            rt_breached_at__isnull=False,
        ).exclude(
            status=Ticket.Status.CLOSED,
        ).count()

        by_status = qs.values('status').annotate(
            count=Count('id'),
        ).order_by('status')
        ctx['by_status'] = {
            s['status']: s['count'] for s in by_status
        }
        ctx['status_choices'] = Ticket.Status.choices

        by_priority = qs.values('priority').annotate(
            count=Count('id'),
        ).order_by('priority')
        ctx['by_priority'] = {
            p['priority']: p['count'] for p in by_priority
        }
        ctx['priority_choices'] = Ticket.Priority.choices

        ctx['recent_tickets'] = (
            qs.select_related(
                'created_by', 'assigned_agent',
            ).order_by('-created_at')[:5]
        )

        return ctx
