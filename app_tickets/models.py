from django.conf import settings
from django.db import models


class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Aberto'
        TRIAGE = 'TRIAGE', 'Triagem'
        IN_PROGRESS = 'IN_PROGRESS', 'Em Andamento'
        WAITING_CUSTOMER = 'WAITING_CUSTOMER', 'Aguardando Cliente'
        RESOLVED = 'RESOLVED', 'Resolvido'
        CLOSED = 'CLOSED', 'Fechado'

    class Priority(models.TextChoices):
        P1 = 'P1', 'P1 — Crítica'
        P2 = 'P2', 'P2 — Alta'
        P3 = 'P3', 'P3 — Média'

    class Category(models.TextChoices):
        GITHUB_REPO = 'GITHUB_REPO', 'Novo Repositório no GitHub'
        GITHUB_USER = 'GITHUB_USER', (
            'Adicionar usuário em um repositório no GitHub'
        )
        SERVICE_OUTAGE = 'SERVICE_OUTAGE', (
            'Reporte de Indisponibilidade de Serviço'
        )
        S3_BUCKET = 'S3_BUCKET', (
            'Criação de Bucket S3 para um projeto'
        )
        OTHER = 'OTHER', 'Outros'

    title = models.CharField('título', max_length=200)
    description = models.TextField('descrição')
    attachment = models.FileField(
        'anexo',
        upload_to='tickets/attachments/%Y/%m/%d/',
        null=True,
        blank=True,
    )
    status = models.CharField(
        'status',
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    priority = models.CharField(
        'prioridade',
        max_length=2,
        choices=Priority.choices,
        default=Priority.P3,
    )
    category = models.CharField(
        'categoria',
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tickets',
        verbose_name='criado por',
    )
    project = models.ForeignKey(
        'app_projects.Project',
        on_delete=models.PROTECT,
        related_name='tickets',
        verbose_name='projeto',
        null=True,  # Initially null for migration compatibility
        blank=True,
    )
    assigned_team = models.ForeignKey(
        'app_teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        verbose_name='time atribuído',
    )
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name='agente atribuído',
    )
    first_response_at = models.DateTimeField(
        'primeira resposta em',
        null=True,
        blank=True,
    )
    resolved_at = models.DateTimeField(
        'resolvido em',
        null=True,
        blank=True,
    )
    closed_at = models.DateTimeField(
        'fechado em',
        null=True,
        blank=True,
    )
    rt_breached_at = models.DateTimeField(
        'RT estourado em',
        null=True,
        blank=True,
    )
    rt_paused_at = models.DateTimeField(
        'RT pausado em',
        null=True,
        blank=True,
    )
    rt_paused_seconds = models.IntegerField(
        'segundos de RT pausado',
        default=0,
    )
    is_escalated = models.BooleanField(
        'escalado',
        default=False,
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'chamado'
        verbose_name_plural = 'chamados'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} — {self.title}'


class Comment(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='chamado',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='autor',
    )
    content = models.TextField('conteúdo')
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'comentário'
        verbose_name_plural = 'comentários'
        ordering = ['created_at']

    def __str__(self):
        return f'Comentário de {self.author.email} em #{self.ticket_id}'


class AuditLog(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        verbose_name='chamado',
    )
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='alterado por',
    )
    changed_by_name = models.CharField(
        'nome de quem alterou',
        max_length=200,
        default='',
    )
    old_status = models.CharField(
        'status anterior',
        max_length=20,
        blank=True,
        default='',
    )
    new_status = models.CharField(
        'novo status',
        max_length=20,
        blank=True,
        default='',
    )
    reason = models.TextField('motivo', blank=True, default='')
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'log de auditoria'
        verbose_name_plural = 'logs de auditoria'
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.ticket_id}: {self.old_status} → {self.new_status}'
