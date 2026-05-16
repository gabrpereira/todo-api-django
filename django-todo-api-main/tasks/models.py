"""
Models for the Task Manager API.

Inclui:
- Category: modelo de categorias para as tarefas (Desafio 01)
- Task: modelo principal com campos de prioridade, status e categoria
"""

from django.db import models
from django.utils import timezone


class Category(models.Model):
    """
    Desafio 01: Model de Categoria relacionada às tarefas.
    Campos:
        - id: chave primária automática
        - name: nome da categoria
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nome'
    )

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Model principal de Tarefas.
    Campos:
        - title: título da tarefa
        - description: descrição detalhada
        - is_done: status de conclusão
        - priority: nível de prioridade (baixa, média, alta)
        - created_at: data de criação automática
        - category: FK para Category (Desafio 01)
    """

    PRIORITY_CHOICES = [
        ('baixa', 'Baixa'),
        ('media', 'Média'),
        ('alta', 'Alta'),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    description = models.TextField(
        blank=True,
        default='',
        verbose_name='Descrição'
    )
    is_done = models.BooleanField(
        default=False,
        verbose_name='Concluída'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='media',
        verbose_name='Prioridade'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Criada em'
    )
    # Desafio 01: ForeignKey para Category
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='Categoria'
    )

    class Meta:
        verbose_name = 'Tarefa'
        verbose_name_plural = 'Tarefas'
        ordering = ['-created_at']

    def __str__(self):
        status = '✅' if self.is_done else '❌'
        return f"[{self.priority.upper()}] {self.title} {status}"

    @property
    def is_overdue(self):
        """Retorna True se a tarefa está atrasada (não concluída e criada há mais de 7 dias)."""
        if self.is_done:
            return False
        limit = timezone.now() - timezone.timedelta(days=7)
        return self.created_at < limit
