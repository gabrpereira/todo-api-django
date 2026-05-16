"""
URL configuration para o app tasks.
Utiliza DefaultRouter do DRF para gerar automaticamente as rotas CRUD
para TaskViewSet e CategoryViewSet.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet

# O DefaultRouter cria automaticamente as rotas:
#   /api/tasks/             -> list, create
#   /api/tasks/{id}/        -> retrieve, update, partial_update, destroy
#   /api/tasks/atrasadas/   -> action customizada (Desafio 02)
#   /api/tasks/{id}/concluir/ -> action customizada
#   /api/tasks/resumo/      -> action customizada
#   /api/categories/        -> list, create
#   /api/categories/{id}/   -> retrieve, update, partial_update, destroy

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]
