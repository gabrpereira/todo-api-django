"""
Serializers para o Task Manager API.

Inclui:
- CategorySerializer: serializa Category com o nome
- TaskSerializer: serializa Task mostrando o nome da categoria (Desafio 01)
  e com validação de prioridade 'alta' (Desafio 03)
"""

from rest_framework import serializers
from django.utils import timezone
from .models import Category, Task


class CategorySerializer(serializers.ModelSerializer):
    """Serializer para o model Category."""

    task_count = serializers.SerializerMethodField(
        help_text='Número de tarefas associadas à categoria'
    )

    class Meta:
        model = Category
        fields = ['id', 'name', 'task_count']

    def get_task_count(self, obj):
        """Retorna a quantidade de tarefas associadas à categoria."""
        return obj.tasks.count()


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer para o model Task.

    Desafio 01: Exibe o nome da categoria ao invés de apenas o ID.
    Desafio 03: Valida que não se pode criar tarefa com priority='alta'
                se já existirem 3 tarefas de alta prioridade não concluídas.
    """

    # Desafio 01: campo de leitura para exibir o nome da categoria
    category_name = serializers.SerializerMethodField(
        help_text='Nome da categoria (somente leitura)'
    )

    # Campo para escrita: aceita o ID da categoria
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        allow_null=True,
        required=False,
        help_text='ID da categoria (use category_id para escrever)'
    )

    # Campo calculado: indica se está atrasada
    is_overdue = serializers.SerializerMethodField(
        help_text='True se não concluída e criada há mais de 7 dias'
    )

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'is_done',
            'priority',
            'created_at',
            'category',       # ID para escrita
            'category_name',  # Nome para leitura (Desafio 01)
            'is_overdue',
        ]
        read_only_fields = ['id', 'created_at', 'is_overdue']

    def get_category_name(self, obj):
        """
        Desafio 01: Retorna o nome da categoria ao invés do ID.
        Retorna None se a tarefa não tem categoria.
        """
        if obj.category:
            return obj.category.name
        return None

    def get_is_overdue(self, obj):
        """Retorna o status de 'atrasada' da tarefa."""
        return obj.is_overdue

    def validate(self, attrs):
        """
        Desafio 03: Valida que não é possível criar tarefa com priority='alta'
        se já existem 3 ou mais tarefas de alta prioridade não concluídas.

        Levanta ValidationError caso a condição seja violada.
        """
        priority = attrs.get('priority')

        # Verificar se é uma criação (sem instância) ou atualização
        instance = self.instance

        # Verifica somente quando a prioridade sendo definida é 'alta'
        if priority == 'alta':
            # Na atualização, excluir a própria tarefa da contagem
            qs = Task.objects.filter(priority='alta', is_done=False)
            if instance:
                qs = qs.exclude(pk=instance.pk)

            count = qs.count()
            if count >= 3:
                raise serializers.ValidationError({
                    'priority': (
                        f'Não é possível criar/atualizar tarefa com prioridade ALTA. '
                        f'Já existem {count} tarefa(s) de alta prioridade não concluídas. '
                        f'Limite: 3 tarefas. Conclua algumas tarefas antes de adicionar novas.'
                    )
                })

        return attrs
