# 📋 Todo API — Organizador de Atividades

Serviço RESTful para controle e acompanhamento de atividades diárias, desenvolvido com **Django REST Framework**.

---

## 🚀 Iniciando a Aplicação

### Requisitos

- Python 3.10 ou superior
- pip (gerenciador de dependências do Python)

### Instruções de Configuração

```bash
# 1. Acesse o diretório do projeto
cd TodoList

# 2. Crie e ative um ambiente virtual isolado
python -m venv venv

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# 3. Instale os pacotes necessários
pip install -r requirements.txt

# 4. Execute as migrações para preparar o banco de dados
python manage.py migrate

# 5. (Opcional) Registre um superusuário para acessar o painel administrativo
python manage.py createsuperuser

# 6. Suba o servidor de desenvolvimento
python manage.py runserver
```

A aplicação ficará acessível em: **http://127.0.0.1:8000/**
Painel Administrativo: **http://127.0.0.1:8000/admin/**

---

## 🗂️ Organização dos Arquivos

```
TodoList/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3               # criado após executar migrate
├── task_manager/            # configurações centrais do projeto Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── tasks/                   # módulo principal da aplicação
    ├── models.py            # Entidades Category e Task
    ├── serializers.py       # Conversores com regras de validação
    ├── views.py             # ViewSets e operações personalizadas
    ├── urls.py              # Mapeamento de rotas via DefaultRouter
    ├── admin.py             # Personalização do painel Django Admin
    └── tests.py             # Suíte de testes automatizados
```

---

## 📡 Rotas da API

### URL Base: `http://127.0.0.1:8000/api/`

---

### 🏷️ Categorias — `/api/categories/`

| Verbo  | Rota                       | Finalidade                           |
|--------|----------------------------|--------------------------------------|
| GET    | `/api/categories/`         | Retorna todas as categorias          |
| POST   | `/api/categories/`         | Registra uma nova categoria          |
| GET    | `/api/categories/{id}/`    | Exibe os dados de uma categoria      |
| PUT    | `/api/categories/{id}/`    | Substitui todos os campos            |
| PATCH  | `/api/categories/{id}/`    | Altera campos específicos            |
| DELETE | `/api/categories/{id}/`    | Apaga uma categoria                  |

---

### ✅ Atividades — `/api/tasks/`

| Verbo  | Rota                            | Finalidade                                         |
|--------|---------------------------------|----------------------------------------------------|
| GET    | `/api/tasks/`                   | Retorna todas as atividades                        |
| POST   | `/api/tasks/`                   | Registra uma nova atividade                        |
| GET    | `/api/tasks/{id}/`              | Exibe os dados de uma atividade                    |
| PUT    | `/api/tasks/{id}/`              | Substitui todos os campos                          |
| PATCH  | `/api/tasks/{id}/`              | Altera campos específicos                          |
| DELETE | `/api/tasks/{id}/`              | Apaga uma atividade                                |
| GET    | `/api/tasks/atrasadas/`         | ⚠️ Retorna atividades fora do prazo (Desafio 02)    |
| POST   | `/api/tasks/{id}/concluir/`     | ✅ Sinaliza uma atividade como finalizada            |
| GET    | `/api/tasks/resumo/`            | 📊 Panorama estatístico das atividades              |

---

### 🔍 Parâmetros de Consulta — Filtros, Pesquisa e Ordenação

A API oferece suporte a filtragem, pesquisa textual e ordenação por meio de query params:

```
# Selecionar por status de conclusão
GET /api/tasks/?is_done=true
GET /api/tasks/?is_done=false

# Selecionar por nível de urgência
GET /api/tasks/?priority=alta
GET /api/tasks/?priority=media
GET /api/tasks/?priority=baixa

# Selecionar por categoria (via ID)
GET /api/tasks/?category=1

# Pesquisa livre no título e na descrição
GET /api/tasks/?search=django

# Definir ordem dos resultados
GET /api/tasks/?ordering=created_at
GET /api/tasks/?ordering=-priority

# Combinação de parâmetros
GET /api/tasks/?priority=alta&is_done=false&ordering=-created_at
```

---

## 📦 Exemplos de Requisição e Resposta

### Registrar Categoria

**POST** `/api/categories/`
```json
{
  "name": "Trabalho"
}
```

**Retorno 201 Created:**
```json
{
  "id": 1,
  "name": "Trabalho",
  "task_count": 0
}
```

---

### Registrar Atividade

**POST** `/api/tasks/`
```json
{
  "title": "Estudar Django REST Framework",
  "description": "Revisar ViewSets, Serializers e Routers",
  "priority": "alta",
  "is_done": false,
  "category": 1
}
```

**Retorno 201 Created:**
```json
{
  "id": 1,
  "title": "Estudar Django REST Framework",
  "description": "Revisar ViewSets, Serializers e Routers",
  "is_done": false,
  "priority": "alta",
  "created_at": "2026-05-08T18:00:00-03:00",
  "category": 1,
  "category_name": "Trabalho",
  "is_overdue": false
}
```

---

### Alteração Parcial de Atividade

**PATCH** `/api/tasks/1/`
```json
{
  "is_done": true
}
```

**Retorno 200 OK:**
```json
{
  "id": 1,
  "title": "Estudar Django REST Framework",
  "is_done": true,
  "priority": "alta",
  "created_at": "2026-05-08T18:00:00-03:00",
  "category": 1,
  "category_name": "Trabalho",
  "is_overdue": false
}
```

---

### Finalizar uma Atividade

**POST** `/api/tasks/1/concluir/`
*(Nenhum corpo necessário na requisição)*

**Retorno 200 OK:**
```json
{
  "detail": "Tarefa marcada como concluída com sucesso!",
  "task": {
    "id": 1,
    "title": "Estudar Django REST Framework",
    "is_done": true,
    ...
  }
}
```

---

### Consultar Atividades Fora do Prazo

**GET** `/api/tasks/atrasadas/`

**Retorno 200 OK:**
```json
{
  "count": 2,
  "limite_data": "2026-05-01T18:00:00-03:00",
  "results": [
    {
      "id": 3,
      "title": "Tarefa Antiga",
      "is_done": false,
      "priority": "media",
      "created_at": "2026-04-20T10:00:00-03:00",
      "category": null,
      "category_name": null,
      "is_overdue": true
    }
  ]
}
```

---

### Panorama Estatístico

**GET** `/api/tasks/resumo/`

**Retorno 200 OK:**
```json
{
  "total": 10,
  "concluidas": 4,
  "pendentes": 6,
  "atrasadas": 2,
  "por_prioridade": {
    "alta": {
      "total": 3,
      "pendentes": 2,
      "vagas_disponiveis": 1,
      "limite_atingido": false
    },
    "media": { "total": 5 },
    "baixa": { "total": 2 }
  }
}
```

---

## ⚠️ Códigos de Resposta e Situações de Erro

| Código | Significado                  | Contexto típico                                       |
|--------|------------------------------|-------------------------------------------------------|
| 200    | Sucesso                      | GET, PATCH, POST /concluir executados corretamente    |
| 201    | Recurso Criado               | POST gerou um novo registro                           |
| 204    | Sem Conteúdo                 | DELETE removeu o registro                             |
| 400    | Requisição Inválida          | Dados inconsistentes ou regra de negócio violada      |
| 404    | Não Localizado               | Recurso inexistente                                   |
| 405    | Verbo Não Permitido          | Método HTTP incompatível com a rota                   |

### Exemplo de Erro — Limite de Prioridade Alta (Desafio 03)

**POST** `/api/tasks/` enviando `priority: "alta"` quando já há 3 atividades urgentes em aberto:

```json
{
  "priority": [
    "Não é possível criar/atualizar tarefa com prioridade ALTA. Já existem 3 tarefa(s) de alta prioridade não concluídas. Limite: 3 tarefas. Conclua algumas tarefas antes de adicionar novas."
  ]
}
```

---

## 🧪 Executando a Suíte de Testes

```bash
# Rodar todos os testes do módulo
python manage.py test tasks

# Rodar com saída detalhada
python manage.py test tasks --verbosity=2
```

**Cenários verificados:**

- ✅ Operações completas (CRUD) de Category
- ✅ Operações completas (CRUD) de Task
- ✅ Desafio 01: exibição do `category_name` no serializer
- ✅ Desafio 02: rota `/atrasadas/` filtrando atividades fora do prazo
- ✅ Desafio 03: restrição de no máximo 3 atividades com urgência `alta` em aberto
- ✅ Operação personalizada `/concluir/`
- ✅ Rota `/resumo/` com dados estatísticos

---

## 🏗️ Desafios Implementados

### Desafio 01 — Entidade Category

- Entidade `Category` composta pelos campos `id` e `name`
- Vínculo `ForeignKey` de `Task` para `Category` (relação muitos-para-um)
- O conversor (serializer) apresenta `category_name` (denominação) além de `category` (identificador numérico)

### Desafio 02 — Rota de Atividades Fora do Prazo

- `@action` denominada `atrasadas` dentro do `TaskViewSet`
- Seleciona atividades com `is_done=False` e `created_at` anterior a 7 dias atrás
- Acesso via: `GET /api/tasks/atrasadas/`

### Desafio 03 — Restrição de Prioridade

- Implementada no método `validate()` do `TaskSerializer`
- Dispara `ValidationError` quando `priority='alta'` e já existem 3 ou mais atividades urgentes pendentes
- Na atualização, a própria instância é excluída da contagem para evitar falsos positivos

### Desafio 04 — Documentação

- Este README.md

---

## 🛠️ Stack Tecnológica

| Tecnologia                  | Versão   | Papel no Projeto                             |
|-----------------------------|----------|----------------------------------------------|
| Python                      | 3.10+    | Linguagem de programação principal           |
| Django                      | 5.0.6    | Framework web de alto nível                  |
| Django REST Framework (DRF) | 3.15.2   | Toolkit para construção de APIs RESTful      |
| django-filter               | 24.2     | Motor de filtragem avançada sobre querysets  |
| SQLite                      | nativo   | Banco de dados relacional (ambiente local)   |

