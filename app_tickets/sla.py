from datetime import timedelta

from django.utils import timezone

from app_tickets.models import Ticket


SLA_TARGETS = {
    Ticket.Priority.P1: {
        'frt': timedelta(minutes=30),
        'rt': timedelta(hours=4),
    },
    Ticket.Priority.P2: {
        'frt': timedelta(hours=2),
        'rt': timedelta(hours=24),
    },
    Ticket.Priority.P3: {
        'frt': timedelta(hours=8),
        'rt': timedelta(hours=72),
    },
}


def calculate_frt(ticket):
    """Return FRT timedelta or None if not yet responded."""
    if ticket.first_response_at:
        return ticket.first_response_at - ticket.created_at
    return None


def calculate_rt(ticket):
    """Return RT timedelta excluding paused time."""
    now = timezone.now()
    end = ticket.resolved_at or now
    total = end - ticket.created_at
    paused = timedelta(seconds=ticket.rt_paused_seconds)

    if ticket.rt_paused_at and not ticket.resolved_at:
        paused += now - ticket.rt_paused_at

    rt = total - paused
    return max(rt, timedelta(0))


def check_sla_status(ticket):
    """Return SLA status dict with breach info."""
    targets = SLA_TARGETS.get(ticket.priority, SLA_TARGETS['P3'])

    frt = calculate_frt(ticket)
    rt = calculate_rt(ticket)

    frt_target = targets['frt']
    rt_target = targets['rt']

    return {
        'frt': frt,
        'frt_target': frt_target,
        'frt_breached': frt is not None and frt > frt_target,
        'frt_pending': frt is None,
        'rt': rt,
        'rt_target': rt_target,
        'rt_breached': rt > rt_target,
    }


def is_rt_breached(ticket):
    """Check if ticket RT exceeds SLA target."""
    targets = SLA_TARGETS.get(ticket.priority, SLA_TARGETS['P3'])
    rt = calculate_rt(ticket)
    return rt > targets['rt']
