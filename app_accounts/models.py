from django.contrib.auth.models import AbstractUser
from django.db import models

from app_accounts.managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'Cliente'
        ADMIN = 'ADMIN', 'Administrador'

    username = None
    email = models.EmailField('e-mail', unique=True)
    role = models.CharField(
        'perfil',
        max_length=10,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    updated_at = models.DateTimeField('atualizado em', auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()
