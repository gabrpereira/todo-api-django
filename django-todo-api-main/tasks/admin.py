"""
Admin configuration para o app tasks.
Registra Task e Category no painel administrativo do Django.
"""

from django.contrib import admin
from .models import Category, Task


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin para o model Category."""
    list_display = ['id', 'name', 'get_task_count']
    search_fields = ['name']
    ordering = ['name']

    @admin.display(description='Nº de Tarefas')
    def get_task_count(self, obj):
        return obj.tasks.count()


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Admin para o model Task com filtros e busca."""
    list_display = [
        'id', 'title', 'priority', 'is_done',
        'category', 'is_overdue_display', 'created_at'
    ]
    list_filter = ['priority', 'is_done', 'category', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['is_done', 'priority']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'description', 'category')
        }),
        ('Status e Prioridade', {
            'fields': ('is_done', 'priority')
        }),
        ('Datas', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Atrasada?', boolean=True)
    def is_overdue_display(self, obj):
        return obj.is_overdue
