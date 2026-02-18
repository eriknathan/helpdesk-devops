from django.utils import timezone

from app_tickets.models import AuditLog, Comment, Ticket


class TransitionError(Exception):
    pass


VALID_TRANSITIONS = {
    Ticket.Status.TRIAGE: [
        Ticket.Status.IN_PROGRESS,
        Ticket.Status.RESOLVED,
    ],
    Ticket.Status.IN_PROGRESS: [
        Ticket.Status.WAITING_CUSTOMER,
        Ticket.Status.RESOLVED,
        Ticket.Status.TRIAGE,
    ],
    Ticket.Status.WAITING_CUSTOMER: [
        Ticket.Status.IN_PROGRESS,
        Ticket.Status.RESOLVED,
    ],
    Ticket.Status.RESOLVED: [
        Ticket.Status.CLOSED,
        Ticket.Status.IN_PROGRESS,
    ],
}

REASON_REQUIRED = {
    Ticket.Status.WAITING_CUSTOMER,
    Ticket.Status.RESOLVED,
}


def transition_ticket(ticket, new_status, user, reason=''):
    old_status = ticket.status
    _validate_transition(ticket, old_status, new_status, user, reason)

    now = timezone.now()

    if new_status == Ticket.Status.WAITING_CUSTOMER:
        ticket.rt_paused_at = now

    if (
        old_status == Ticket.Status.WAITING_CUSTOMER
        and new_status == Ticket.Status.IN_PROGRESS
    ):
        if ticket.rt_paused_at:
            paused = (now - ticket.rt_paused_at).total_seconds()
            ticket.rt_paused_seconds += int(paused)
            ticket.rt_paused_at = None

    if new_status == Ticket.Status.RESOLVED:
        ticket.resolved_at = now

    if new_status == Ticket.Status.CLOSED:
        ticket.closed_at = now

    if (
        old_status == Ticket.Status.RESOLVED
        and new_status == Ticket.Status.IN_PROGRESS
    ):
        ticket.resolved_at = None

    ticket.status = new_status
    ticket.save()

    AuditLog.objects.create(
        ticket=ticket,
        changed_by=user,
        changed_by_name=user.full_name or user.email,
        old_status=old_status,
        new_status=new_status,
        reason=reason,
    )


def _validate_transition(ticket, old_status, new_status, user, reason):
    allowed = VALID_TRANSITIONS.get(old_status, [])
    if new_status not in allowed:
        raise TransitionError(
            f'Transição de {old_status} para {new_status} '
            f'não é permitida.'
        )

    is_reopen = (
        old_status == Ticket.Status.RESOLVED
        and new_status == Ticket.Status.IN_PROGRESS
    )

    if is_reopen:
        _validate_reopen(ticket, user, reason)
    elif user.is_customer:
        raise TransitionError(
            'Apenas administradores podem alterar o status.'
        )

    if new_status in REASON_REQUIRED and not reason.strip():
        raise TransitionError(
            'É necessário informar um motivo para esta transição.'
        )

    if (
        old_status == Ticket.Status.TRIAGE
        and new_status == Ticket.Status.IN_PROGRESS
    ):
        _validate_assignment(ticket)

    if (
        old_status == Ticket.Status.RESOLVED
        and new_status == Ticket.Status.CLOSED
    ):
        _validate_close(ticket, user)


def _validate_assignment(ticket):
    if not ticket.assigned_team_id:
        raise TransitionError(
            'É necessário atribuir um time antes de iniciar.'
        )
    if not ticket.assigned_agent_id:
        raise TransitionError(
            'É necessário atribuir um responsável antes de iniciar.'
        )
    if not ticket.assigned_agent.is_active:
        raise TransitionError(
            'O responsável atribuído está inativo.'
        )


def _validate_close(ticket, user):
    if not user.is_admin:
        raise TransitionError(
            'Apenas administradores podem fechar chamados.'
        )
    has_admin_comment = Comment.objects.filter(
        ticket=ticket,
        author__role='ADMIN',
    ).exists()
    if not has_admin_comment:
        raise TransitionError(
            'É necessário ao menos um comentário de administrador '
            'para fechar o chamado.'
        )


def _validate_reopen(ticket, user, reason):
    if not reason.strip():
        raise TransitionError(
            'É necessário informar um motivo para reabrir.'
        )
    if not ticket.resolved_at:
        raise TransitionError(
            'Chamado não possui data de resolução.'
        )
    days_since = (timezone.now() - ticket.resolved_at).days
    if days_since > 7:
        raise TransitionError(
            'Não é possível reabrir chamados resolvidos há mais de 7 dias.'
        )
    has_customer_comment = Comment.objects.filter(
        ticket=ticket,
        author__role='CUSTOMER',
        created_at__gt=ticket.resolved_at,
    ).exists()
    if not has_customer_comment:
        raise TransitionError(
            'É necessário um comentário do cliente após a resolução '
            'para reabrir o chamado.'
        )
