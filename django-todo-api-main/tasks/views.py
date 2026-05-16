"""
Views para o Task Manager API usando ViewSets do Django REST Framework.

Inclui:
- CategoryViewSet: CRUD completo para categorias
- TaskViewSet: CRUD completo para tarefas com actions customizadas:
    - atrasadas (Desafio 02): retorna tarefas não concluídas criadas há mais de 7 dias
    - concluir: marca uma tarefa como concluída via POST
    - resumo: retorna estatísticas gerais das tarefas
"""

from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Task
from .serializers import CategorySerializer, TaskSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Categorias.

    list:   GET  /api/categories/          - Lista todas as categorias
    create: POST /api/categories/          - Cria nova categoria
    retrieve: GET /api/categories/{id}/    - Detalha uma categoria
    update: PUT  /api/categories/{id}/     - Atualiza categoria completa
    partial_update: PATCH /api/categories/{id}/ - Atualiza categoria parcialmente
    destroy: DELETE /api/categories/{id}/ - Remove uma categoria
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'id']
    ordering = ['name']


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciar Tarefas.

    list:   GET  /api/tasks/               - Lista todas as tarefas
    create: POST /api/tasks/               - Cria nova tarefa
    retrieve: GET /api/tasks/{id}/         - Detalha uma tarefa
    update: PUT  /api/tasks/{id}/          - Atualiza tarefa completa
    partial_update: PATCH /api/tasks/{id}/ - Atualiza tarefa parcialmente
    destroy: DELETE /api/tasks/{id}/       - Remove uma tarefa

    Actions customizadas:
    atrasadas: GET /api/tasks/atrasadas/   - Lista tarefas atrasadas (Desafio 02)
    concluir:  POST /api/tasks/{id}/concluir/ - Marca tarefa como concluída
    resumo:    GET /api/tasks/resumo/      - Retorna resumo/estatísticas
    """
    queryset = Task.objects.select_related('category').all()
    serializer_class = TaskSerializer

    # Filtros e busca
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_done', 'priority', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'priority', 'title']
    ordering = ['-created_at']

    # ---------------------------------------------------------------
    # Desafio 02: Action para tarefas atrasadas
    # ---------------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='atrasadas')
    def atrasadas(self, request):
        """
        Desafio 02: Retorna tarefas atrasadas.

        Uma tarefa é considerada atrasada quando:
        - is_done = False (não concluída)
        - created_at < timezone.now() - 7 dias (criada há mais de 7 dias)

        GET /api/tasks/atrasadas/
        """
        limite = timezone.now() - timezone.timedelta(days=7)

        tarefas_atrasadas = Task.objects.filter(
            is_done=False,
            created_at__lt=limite
        ).select_related('category')

        serializer = self.get_serializer(tarefas_atrasadas, many=True)

        return Response({
            'count': tarefas_atrasadas.count(),
            'limite_data': limite.isoformat(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)

    # ---------------------------------------------------------------
    # Action extra: Concluir tarefa
    # ---------------------------------------------------------------
    @action(detail=True, methods=['post'], url_path='concluir')
    def concluir(self, request, pk=None):
        """
        Marca uma tarefa específica como concluída (is_done=True).

        POST /api/tasks/{id}/concluir/
        """
        task = self.get_object()

        if task.is_done:
            return Response(
                {'detail': 'Esta tarefa já está concluída.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.is_done = True
        task.save()

        serializer = self.get_serializer(task)
        return Response({
            'detail': 'Tarefa marcada como concluída com sucesso!',
            'task': serializer.data
        }, status=status.HTTP_200_OK)

    # ---------------------------------------------------------------
    # Action extra: Resumo/Estatísticas
    # ---------------------------------------------------------------
    @action(detail=False, methods=['get'], url_path='resumo')
    def resumo(self, request):
        """
        Retorna um resumo estatístico das tarefas.

        GET /api/tasks/resumo/
        """
        total = Task.objects.count()
        concluidas = Task.objects.filter(is_done=True).count()
        pendentes = Task.objects.filter(is_done=False).count()

        # Por prioridade
        alta_total = Task.objects.filter(priority='alta').count()
        alta_pendente = Task.objects.filter(priority='alta', is_done=False).count()
        media_total = Task.objects.filter(priority='media').count()
        baixa_total = Task.objects.filter(priority='baixa').count()

        # Atrasadas
        limite = timezone.now() - timezone.timedelta(days=7)
        atrasadas = Task.objects.filter(is_done=False, created_at__lt=limite).count()

        # Vagas disponíveis de prioridade alta
        vagas_alta = max(0, 3 - alta_pendente)

        return Response({
            'total': total,
            'concluidas': concluidas,
            'pendentes': pendentes,
            'atrasadas': atrasadas,
            'por_prioridade': {
                'alta': {
                    'total': alta_total,
                    'pendentes': alta_pendente,
                    'vagas_disponiveis': vagas_alta,
                    'limite_atingido': alta_pendente >= 3,
                },
                'media': {'total': media_total},
                'baixa': {'total': baixa_total},
            },
        }, status=status.HTTP_200_OK)
