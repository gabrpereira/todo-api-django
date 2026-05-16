"""
Testes para o Task Manager API.

Cobre:
- CRUD de Category e Task
- Desafio 01: serializer mostra category_name
- Desafio 02: endpoint /api/tasks/atrasadas/
- Desafio 03: validação de prioridade 'alta' (máx 3 pendentes)
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .models import Category, Task


class CategoryAPITest(TestCase):
    """Testes para o endpoint de Categorias."""

    def setUp(self):
        self.client = APIClient()
        self.categoria = Category.objects.create(name='Trabalho')

    def test_listar_categorias(self):
        """GET /api/categories/ deve retornar lista de categorias."""
        response = self.client.get('/api/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_criar_categoria(self):
        """POST /api/categories/ deve criar nova categoria."""
        response = self.client.post('/api/categories/', {'name': 'Pessoal'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Pessoal')

    def test_detalhar_categoria(self):
        """GET /api/categories/{id}/ deve retornar detalhes."""
        response = self.client.get(f'/api/categories/{self.categoria.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Trabalho')

    def test_atualizar_categoria(self):
        """PATCH /api/categories/{id}/ deve atualizar o nome."""
        response = self.client.patch(
            f'/api/categories/{self.categoria.id}/',
            {'name': 'Trabalho Atualizado'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Trabalho Atualizado')

    def test_deletar_categoria(self):
        """DELETE /api/categories/{id}/ deve remover a categoria."""
        response = self.client.delete(f'/api/categories/{self.categoria.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class TaskAPITest(TestCase):
    """Testes para o endpoint de Tarefas."""

    def setUp(self):
        self.client = APIClient()
        self.categoria = Category.objects.create(name='Estudos')
        self.task = Task.objects.create(
            title='Estudar DRF',
            description='Aprender Django REST Framework',
            priority='media',
            category=self.categoria
        )

    def test_listar_tasks(self):
        """GET /api/tasks/ deve retornar lista de tarefas."""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 1)

    def test_criar_task(self):
        """POST /api/tasks/ deve criar nova tarefa."""
        payload = {
            'title': 'Nova Tarefa',
            'description': 'Descrição da nova tarefa',
            'priority': 'baixa',
            'category': self.categoria.id
        }
        response = self.client.post('/api/tasks/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Nova Tarefa')

    def test_detalhar_task(self):
        """GET /api/tasks/{id}/ deve retornar detalhes."""
        response = self.client.get(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Estudar DRF')

    def test_atualizar_task(self):
        """PATCH /api/tasks/{id}/ deve atualizar parcialmente."""
        response = self.client.patch(
            f'/api/tasks/{self.task.id}/',
            {'is_done': True}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_done'])

    def test_deletar_task(self):
        """DELETE /api/tasks/{id}/ deve remover a tarefa."""
        response = self.client.delete(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class Desafio01CategoryNameTest(TestCase):
    """
    Desafio 01: Testa se o serializer retorna category_name
    ao invés de apenas o ID da categoria.
    """

    def setUp(self):
        self.client = APIClient()
        self.categoria = Category.objects.create(name='Saúde')
        self.task = Task.objects.create(
            title='Fazer exercícios',
            priority='alta',
            category=self.categoria
        )

    def test_serializer_exibe_category_name(self):
        """O campo category_name deve exibir o nome da categoria."""
        response = self.client.get(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Desafio 01: verificar que category_name está presente e correto
        self.assertIn('category_name', response.data)
        self.assertEqual(response.data['category_name'], 'Saúde')

    def test_task_sem_categoria_exibe_none(self):
        """Tarefa sem categoria deve retornar category_name como null."""
        task_sem_cat = Task.objects.create(
            title='Tarefa sem categoria',
            priority='baixa'
        )
        response = self.client.get(f'/api/tasks/{task_sem_cat.id}/')
        self.assertIsNone(response.data['category_name'])


class Desafio02AtrasadasTest(TestCase):
    """
    Desafio 02: Testa o endpoint /api/tasks/atrasadas/
    que retorna tarefas com is_done=False e created_at > 7 dias.
    """

    def setUp(self):
        self.client = APIClient()

        # Tarefa atrasada: criada há 10 dias, não concluída
        self.task_atrasada = Task.objects.create(
            title='Tarefa Atrasada',
            priority='media',
            is_done=False,
            created_at=timezone.now() - timedelta(days=10)
        )

        # Tarefa recente: criada há 3 dias, não concluída (NÃO atrasada)
        self.task_recente = Task.objects.create(
            title='Tarefa Recente',
            priority='media',
            is_done=False,
            created_at=timezone.now() - timedelta(days=3)
        )

        # Tarefa atrasada MAS concluída (NÃO deve aparecer)
        self.task_concluida = Task.objects.create(
            title='Tarefa Concluída Atrasada',
            priority='baixa',
            is_done=True,
            created_at=timezone.now() - timedelta(days=15)
        )

    def test_endpoint_atrasadas_existe(self):
        """GET /api/tasks/atrasadas/ deve retornar 200."""
        response = self.client.get('/api/tasks/atrasadas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retorna_apenas_tarefas_atrasadas(self):
        """Deve retornar apenas tarefas não concluídas criadas há mais de 7 dias."""
        response = self.client.get('/api/tasks/atrasadas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids_retornados = [t['id'] for t in response.data['results']]

        # Tarefa atrasada deve aparecer
        self.assertIn(self.task_atrasada.id, ids_retornados)

        # Tarefa recente NÃO deve aparecer
        self.assertNotIn(self.task_recente.id, ids_retornados)

        # Tarefa concluída NÃO deve aparecer
        self.assertNotIn(self.task_concluida.id, ids_retornados)

    def test_response_tem_count_e_limite_data(self):
        """A resposta deve conter 'count' e 'limite_data'."""
        response = self.client.get('/api/tasks/atrasadas/')
        self.assertIn('count', response.data)
        self.assertIn('limite_data', response.data)
        self.assertEqual(response.data['count'], 1)


class Desafio03ValidacaoPrioridadeTest(TestCase):
    """
    Desafio 03: Testa a validação de prioridade 'alta'.
    Não deve ser possível criar tarefa 'alta' se já existem 3 não concluídas.
    """

    def setUp(self):
        self.client = APIClient()

        # Criar 3 tarefas de alta prioridade não concluídas
        for i in range(1, 4):
            Task.objects.create(
                title=f'Tarefa Alta {i}',
                priority='alta',
                is_done=False
            )

    def test_rejeita_quarta_tarefa_alta(self):
        """Deve retornar 400 ao tentar criar 4ª tarefa de alta prioridade."""
        payload = {
            'title': 'Quarta Tarefa Alta',
            'priority': 'alta',
            'is_done': False
        }
        response = self.client.post('/api/tasks/', payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('priority', response.data)

    def test_permite_criar_tarefa_media_quando_alta_cheio(self):
        """Deve permitir criar tarefa 'media' mesmo com 3 tarefas 'alta' pendentes."""
        payload = {
            'title': 'Tarefa Média Permitida',
            'priority': 'media',
            'is_done': False
        }
        response = self.client.post('/api/tasks/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_permite_criar_alta_apos_concluir_uma(self):
        """Após concluir 1 tarefa alta, deve permitir criar nova."""
        # Concluir uma das tarefas altas
        task_alta = Task.objects.filter(priority='alta', is_done=False).first()
        task_alta.is_done = True
        task_alta.save()

        # Agora deve ser possível criar nova alta (somente 2 pendentes)
        payload = {
            'title': 'Nova Alta Permitida',
            'priority': 'alta',
            'is_done': False
        }
        response = self.client.post('/api/tasks/', payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_action_concluir_task(self):
        """POST /api/tasks/{id}/concluir/ deve marcar tarefa como concluída."""
        task = Task.objects.create(title='Para Concluir', priority='baixa')
        response = self.client.post(f'/api/tasks/{task.id}/concluir/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertTrue(task.is_done)

    def test_action_concluir_tarefa_ja_concluida(self):
        """Tentar concluir tarefa já concluída deve retornar 400."""
        task = Task.objects.create(
            title='Já Concluída', priority='baixa', is_done=True
        )
        response = self.client.post(f'/api/tasks/{task.id}/concluir/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ResumoEndpointTest(TestCase):
    """Testa o endpoint de resumo/estatísticas."""

    def setUp(self):
        self.client = APIClient()
        Task.objects.create(title='T1', priority='alta', is_done=False)
        Task.objects.create(title='T2', priority='alta', is_done=True)
        Task.objects.create(title='T3', priority='media', is_done=False)
        Task.objects.create(title='T4', priority='baixa', is_done=False)

    def test_resumo_retorna_estatisticas(self):
        """GET /api/tasks/resumo/ deve retornar dados estatísticos."""
        response = self.client.get('/api/tasks/resumo/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total', response.data)
        self.assertIn('concluidas', response.data)
        self.assertIn('pendentes', response.data)
        self.assertIn('atrasadas', response.data)
        self.assertIn('por_prioridade', response.data)
        self.assertEqual(response.data['total'], 4)
        self.assertEqual(response.data['concluidas'], 1)
        self.assertEqual(response.data['pendentes'], 3)
