from django import template

register = template.Library()

STATUS_CLASSES = {
    'OPEN': 'bg-sky-100 text-sky-700',
    'TRIAGE': 'bg-amber-100 text-amber-700',
    'IN_PROGRESS': 'bg-violet-100 text-violet-700',
    'WAITING_CUSTOMER': 'bg-orange-100 text-orange-700',
    'RESOLVED': 'bg-emerald-100 text-emerald-700',
    'CLOSED': 'bg-slate-100 text-slate-600',
}

STATUS_LABELS = {
    'OPEN': 'Aberto',
    'TRIAGE': 'Triagem',
    'IN_PROGRESS': 'Em Andamento',
    'WAITING_CUSTOMER': 'Aguardando Cliente',
    'RESOLVED': 'Resolvido',
    'CLOSED': 'Fechado',
}

PRIORITY_CLASSES = {
    'P1': 'bg-rose-100 text-rose-700',
    'P2': 'bg-amber-100 text-amber-700',
    'P3': 'bg-sky-100 text-sky-700',
}

PRIORITY_LABELS = {
    'P1': 'P1 — Crítica',
    'P2': 'P2 — Alta',
    'P3': 'P3 — Média',
}


@register.inclusion_tag('components/badge.html')
def status_badge(status):
    return {
        'label': STATUS_LABELS.get(status, status),
        'classes': STATUS_CLASSES.get(status, 'bg-gray-100 text-gray-600'),
    }


@register.inclusion_tag('components/badge.html')
def priority_badge(priority):
    return {
        'label': PRIORITY_LABELS.get(priority, priority),
        'classes': PRIORITY_CLASSES.get(
            priority, 'bg-gray-100 text-gray-600',
        ),
    }


@register.filter
def dict_get(d, key):
    if isinstance(d, dict):
        return d.get(key, 0)
    return 0
