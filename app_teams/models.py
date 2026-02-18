from django.conf import settings
from django.db import models


class Team(models.Model):
    class Level(models.TextChoices):
        N1 = 'N1', 'Nível 1'
        N2 = 'N2', 'Nível 2'

    name = models.CharField('nome', max_length=100, unique=True)
    description = models.TextField('descrição', blank=True, default='')
    level = models.CharField(
        'nível',
        max_length=2,
        choices=Level.choices,
        default=Level.N1,
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'time'
        verbose_name_plural = 'times'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_level_display()})'


class TeamMember(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name='time',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team_memberships',
        verbose_name='usuário',
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'membro do time'
        verbose_name_plural = 'membros do time'
        unique_together = ['team', 'user']

    def __str__(self):
        return f'{self.user.email} — {self.team.name}'
