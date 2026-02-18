from django.conf import settings
from django.db import models


class Project(models.Model):
    name = models.CharField('nome', max_length=150, unique=True)
    description = models.TextField('descrição', blank=True, default='')
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='projects',
        verbose_name='membros',
    )
    is_active = models.BooleanField('ativo', default=True)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    class Meta:
        verbose_name = 'projeto'
        verbose_name_plural = 'projetos'
        ordering = ['name']

    def __str__(self):
        return self.name
