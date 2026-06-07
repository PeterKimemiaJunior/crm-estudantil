# CRM Estudantil UEM

> Módulo customizado sobre Odoo 17 para gestão do relacionamento entre estudantes e oportunidades académicas/profissionais.  
> Desenvolvido para a disciplina de **Programação Web e CMS** — Engenharia Informática, UEM.

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Stack Tecnológica](#stack-tecnológica)
3. [Estrutura do Projecto](#estrutura-do-projecto)
4. [Como Correr](#como-correr)
5. [Base de Dados](#base-de-dados)
6. [Páginas e Rotas](#páginas-e-rotas)
7. [Popular a Base de Dados (Seed)](#popular-a-base-de-dados-seed)
8. [Avaliação Crítica vs SRS](#avaliação-crítica-vs-srs)

---

## Visão Geral

O **CRM Estudantil** é uma plataforma que conecta dois mundos:

- **CMS (Website público):** Estudantes consultam oportunidades (estágios, eventos, pós-graduações), submetem candidaturas e respondem a questionários de satisfação — tudo sem precisar de conta no sistema.
- **CRM (Backoffice):** Gestores académicos acompanham os candidatos no pipeline Kanban do Odoo, analisam perfis e gerem o ciclo de vida de cada oportunidade.

---

## Stack Tecnológica

| Camada               | Tecnologia                          |
| -------------------- | ----------------------------------- |
| Infraestrutura       | Docker 24+, Docker Compose v2       |
| Base de Dados        | PostgreSQL 15 (contentor `db`)      |
| Backend / ORM        | Python 3.10, Odoo 17.0              |
| Templates / Vistas   | QWeb (XML)                          |
| Frontend Interactivo | JavaScript (fetch/AJAX, DOM nativo) |
| Estilos              | SCSS / CSS (variáveis CSS custom)   |
| Questionários        | Módulo nativo `survey` do Odoo      |

---

## Estrutura do Projecto

```
odoo_project/
├── docker-compose.yml          # Orquestração dos contentores
├── seed_runner.py              # Script de dados mockados
├── custom_addons/
│   └── crm_estudantil/
│       ├── __manifest__.py     # Declaração do módulo
│       ├── __init__.py
│       ├── models/
│       │   ├── crm_lead_ext.py         # Extensão do crm.lead com campos estudantis
│       │   ├── crm_oportunidade_ext.py # Modelo crm.oportunidades (custom)
│       │   └── crm_faq.py              # Modelo de suporte/FAQ
│       ├── controllers/
│       │   ├── main.py                 # Rotas do portal estudantil (/portal)
│       │   ├── survey.py               # Rota de questionários
│       │   ├── gestao_canditatos.py    # Rotas de gestão de candidatos (admin)
│       │   └── gestao.py               # Rotas do Backoffice/Gestão (/gestao)
│       ├── views/
│       │   ├── website_layout.xml          # Layout da gestão (Sidebar)
│       │   ├── portal_layout.xml           # Layout do estudante (Navbar)
│       │   ├── portal_home.xml             # Landing page do portal
│       │   ├── website_oportunidades.xml   # Listagem de oportunidades
│       │   ├── website_candidatura.xml     # Formulário de candidatura
│       │   ├── website_faq.xml             # Suporte & FAQ (Renderização dinâmica)
│       │   ├── website_kanban.xml          # Kanban público
│       │   ├── website_questionarios.xml   # Listagem de questionários
│       │   ├── gestao_home.xml             # Dashboard de gestão
│       │   ├── gestao_candidaturas.xml     # Kanban de candidaturas (admin)
│       │   ├── gestao_oportunidades.xml    # Gestão de oportunidades (admin)
│       │   └── crm_faq_views.xml           # Vistas de backend para o modelo FAQ
│       ├── data/
│       │   └── crm_stages.xml          # Estágios CRM (New/Qualified/Won/Lost)
│       └── static/src/css/
│           └── custom_theme.scss       # Estilos SCSS globais
```

---

## Como Correr

### Pré-requisitos

- Docker Engine 24+
- Docker Compose v2

### Iniciar o Sistema

```bash
# Clonar o repositório
git clone <url-do-repositorio>
cd odoo_project

# Iniciar os contentores (primeira vez — demora ~2 min)
docker compose up -d

# Ver logs do servidor Odoo
docker compose logs -f web
```

O sistema fica disponível em **http://localhost:8069**

### Credenciais de Acesso (Backend Odoo)

| Campo      | Valor                     |
| ---------- | ------------------------- |
| URL        | http://localhost:8069/web |
| Utilizador | `admin`                   |
| Password   | `admin`                   |

### Comandos Úteis

```bash
# Parar os contentores
docker compose down

# Reiniciar apenas o Odoo (limpa cache de templates)
docker compose restart web

# Atualizar o módulo após alterações em XML/Python
docker compose exec web odoo \
  --addons-path=/mnt/custom_addons,/usr/lib/python3/dist-packages/odoo/addons \
  --db_host=db --db_user=odoo --db_password=odoo \
  -d crm_estudantil -u crm_estudantil --stop-after-init

# Limpar cache de assets (se surgir erro AssetsLoadingError)
docker compose exec -T db psql -U odoo -d crm_estudantil \
  -c "DELETE FROM ir_attachment WHERE name ILIKE '%assets%';"
docker compose restart web
```

---

## Base de Dados

O Odoo usa **PostgreSQL** e mapeia automaticamente classes Python em tabelas SQL.

### Modelos Customizados

#### `crm.oportunidades` → tabela `crm_oportunidades`

| Campo                | Tipo                  | Descrição                                         |
| -------------------- | --------------------- | ------------------------------------------------- |
| `name`               | Char                  | Título da oportunidade                            |
| `company_name`       | Char                  | Empresa/entidade                                  |
| `description`        | Text                  | Descrição detalhada                               |
| `opportunity_type`   | Selection             | `estagio` / `posgraduacao` / `evento` / `suporte` |
| `deadline`           | Date                  | Prazo de candidatura                              |
| `active`             | Boolean               | Se está activa (visível no site)                  |
| `candidaturas_ids`   | One2many → `crm.lead` | Candidatos ligados                                |
| `total_candidaturas` | Integer (computed)    | Contagem automática de candidatos                 |

#### `crm.lead` (extensão) → tabela `crm_lead`

Campos adicionados ao modelo nativo do Odoo:

| Campo              | Tipo                           | Descrição                |
| ------------------ | ------------------------------ | ------------------------ |
| `student_number`   | Char                           | Número de estudante UEM  |
| `opportunity_type` | Selection                      | Tipo da candidatura      |
| `course`           | Selection                      | Curso do estudante       |
| `year`             | Integer                        | Ano curricular           |
| `oportunidade_id`  | Many2one → `crm.oportunidades` | Vaga a que se candidatou |
| `color`            | Integer (computed)             | Cor no Kanban (por tipo) |

### Diagrama de Relacionamento

```
crm_oportunidades (1) ──────── (N) crm_lead
      │                              │
      │ id, name, type, deadline     │ id, contact_name, student_number
      │ company_name, description    │ course, year, oportunidade_id
      │ total_candidaturas           │ stage_id, email_from
      └──────────────────────────────┘
                                     │
                             (N) ────┘──── (1) crm_stage
                                          (New/Qualified/Won/Lost)
```

### Tabelas do Módulo `survey` (nativo Odoo)

| Tabela              | Descrição                                    |
| ------------------- | -------------------------------------------- |
| `survey_survey`     | Questionários criados                        |
| `survey_question`   | Perguntas de cada questionário               |
| `survey_user_input` | Respostas individuais (uma por participante) |

### Inspecção Directa via SQL

```bash
# Entrar no PostgreSQL
docker compose exec -T db psql -U odoo -d crm_estudantil

# Exemplos de queries
SELECT name, opportunity_type, deadline FROM crm_oportunidades;
SELECT contact_name, student_number, course FROM crm_lead WHERE student_number IS NOT NULL;
SELECT title FROM survey_survey WHERE active = true;
```

---

### 🎓 Portal do Estudante (Páginas Públicas com Navbar)

| Rota                           | Descrição                                                       | View                        |
| ------------------------------ | --------------------------------------------------------------- | --------------------------- |
| `GET /portal`                  | Landing page do portal estudantil                               | `portal_home`               |
| `GET /portal/oportunidades`    | Listagem de vagas activas com filtros por tipo e pesquisa       | `page_oportunidades`        |
| `GET /portal/candidatura`      | Formulário de candidatura (pré-preenchido se `lead_id` passado) | `page_candidatura`          |
| `GET /portal/faq`              | Suporte académico renderizado dinamicamente via BD              | `page_faq`                  |
| `GET /portal/questionarios`    | Listagem dos questionários disponíveis                          | `page_questionarios`        |

### 🔒 Páginas de Gestão (Backoffice com Sidebar, Requer Login Odoo)

| Rota                                | Descrição                                         | View                               |
| ----------------------------------- | ------------------------------------------------- | ---------------------------------- |
| `GET /gestao/dashboard`             | Dashboard de resumo das oportunidades             | `gestao_home`                      |
| `GET /gestao/oportunidades`         | Lista de oportunidades com contagem de candidatos | `gestao_oportunidades`             |
| `GET /gestao/kanban`                | Vista Kanban das oportunidades                    | `page_kanban`                      |
| `GET /gestao/criar-oportunidade`    | Formulário de criação de nova oportunidade        | `page_criar_oportunidade`          |
| `GET /gestao/candidaturas`          | Kanban de todas as candidaturas por estágio       | `page_gestao_candidaturas`         |
| `GET /gestao/oportunidades/<id>`    | Detalhe da oportunidade com lista de candidatos   | `page_gestao_oportunidade_detalhe` |
| `GET /gestao/candidatos/<id>`       | Perfil completo de um candidato                   | `page_gestao_candidato_detalhe`    |

### ⚙️ API Endpoints (JSON-RPC)

| Rota                          | Método | Descrição                                               |
| ----------------------------- | ------ | ------------------------------------------------------- |
| `/crm_estudantil/submit_lead` | `POST` | Submete uma candidatura (chamado pelo JS do formulário) |
| `/api/oportunidades/create`   | `POST` | Cria uma nova oportunidade                              |
| `/api/candidaturas/move`      | `POST` | Move candidatura entre estágios (Kanban drag-and-drop)  |

---

## Popular a Base de Dados (Seed)

O projecto inclui o script `seed_runner.py` para popular a BD com dados de demonstração.

```bash
# Copiar o script para o contentor e executar
docker compose cp seed_runner.py web:/tmp/seed_runner.py
docker compose exec -T web python3 /tmp/seed_runner.py
```

### Dados Inseridos pelo Seed

| Entidade      | Quantidade | Detalhes                                             |
| ------------- | ---------- | ---------------------------------------------------- |
| Oportunidades | 8          | 3 estágios, 2 pós-graduações, 2 eventos, 1 suporte   |
| Candidatos    | 13         | Estudantes de Informática, Gestão, Direito, Economia |
| Questionários | 3          | Activos e acessíveis publicamente                    |

---

## Avaliação Crítica vs SRS

### ✅ Requisitos Implementados

| Ref.   | Requisito                                                                | Estado                                    |
| ------ | ------------------------------------------------------------------------ | ----------------------------------------- |
| RF-01  | Campos `student_number`, `course`, `year` no `crm.lead`                  | ✅ Implementado                           |
| RF-02  | Campo `opportunity_type` (Estágio/Pós-Grad./Evento/Suporte)              | ✅ Implementado                           |
| RF-03  | Pipeline Kanban com cores por tipo de oportunidade                       | ✅ Implementado (campo `color` computado) |
| RF-04  | Página pública de Oportunidades                                          | ✅ Implementado (`/oportunidades`)        |
| RF-05  | Formulário interactivo de candidatura                                    | ✅ Implementado (`/candidatura`)          |
| RF-06  | Submissão via JavaScript/AJAX sem reload                                 | ✅ Implementado (`fetch` + JSON-RPC)      |
| RF-07  | Criação automática de `crm.lead` com estado "Novo"                       | ✅ Implementado                           |
| RF-08  | Página de Suporte/FAQ                                                    | ✅ Implementado (`/faq`)                  |
| RF-09  | Filtro de pesquisa interactivo no FAQ                                    | ✅ Implementado                           |
| RF-10  | Integração com módulo nativo `survey`                                    | ✅ Implementado (`/questionarios`)        |
| RF-11  | Gestor gera link de questionário e envia por email para contactos do CRM | ✅ Implementado (via Wizard no backend)   |
| RNF-01 | Sistema executado via Docker Compose                                     | ✅ Implementado                           |
| RNF-04 | Código apenas em `custom_addons/crm_estudantil/`                         | ✅ Respeitado                             |

### ⚠️ Requisitos Parcialmente Implementados

| Ref.   | Requisito                                               | Lacuna                                                                                                                                                                                                                                                  |
| ------ | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| RNF-02 | Hot-reload (`--dev=reload`)                             | ⚠️ A flag está configurada no `docker-compose.yml`, mas alterações em XML **exigem** atualização manual do módulo (`-u crm_estudantil`) para que o Odoo recarregue as views da BD. O hot-reload cobre apenas ficheiros Python e assets estáticos.       |
| RNF-03 | Formulário público com validação e sanitização de input | ⚠️ Existe validação no frontend (JavaScript), mas a **validação server-side** no controlador Python é mínima — verifica apenas se `nome` e `email` foram passados, sem sanitização robusta contra injecção ou validação de formato de email no backend. |

### ❌ Problemas e Dívida Técnica (Resolvidos e Restantes)

~~**1. Duplicação de rotas e vistas**~~ (Resolvido)
As rotas foram unificadas. O tráfego dos estudantes flui unicamente por `/portal/...` e a gestão administrativa usa exclusivamente `/gestao/...`. As vistas legadas do portal e ficheiros inúteis (`portal.py`) foram eliminadas.

~~**2. Rotas de gestão sem verificação de perfil**~~ (Resolvido)
Todas as rotas sob `/gestao/...` exigem agora o grupo `base.group_user`, barrando publicamente utilizadores não autenticados de aceder a dashboards e funis de vendas.

**3. Bug de cache de assets em Docker**
Ao reiniciar o ambiente Docker (ex: após `docker compose down && up`), surgem erros do tipo `AssetsLoadingError` porque os registos em `ir_attachment` apontam para ficheiros do filestore que já não existem. Requer limpeza manual via SQL. Este é um problema de arquitectura do ambiente de desenvolvimento que deveria ter um script de reset automatizado.

**4. Typo no nome de ficheiro de controller**
O ficheiro `gestao_canditatos.py` tem um erro ortográfico ("canditatos" em vez de "candidatos"). Pequeno detalhe que carece de correcção para manter a excelência técnica.

~~**5. `survey.public_url` inexistente no Odoo 17**~~ (Resolvido)
A integração com Inquéritos utiliza agora o método nativo mais recente (`get_start_url()`) substituindo código legado quebrado.

**6. Nova Funcionalidade:** As FAQs deixaram de ser estáticas. É agora utilizado um modelo `crm.faq` persistido em Base de Dados. Os gestores podem fazer CRUD a perguntas frequentes via backoffice.

### 📊 Pontuação Global (estimativa honesta)

| Critério                      | Peso     | Nota                                                           |
| ----------------------------- | -------- | -------------------------------------------------------------- |
| Cobertura dos RF do SRS       | 30%      | 9/10 — 11 de 11 RF implementados                               |
| Qualidade técnica do código   | 25%      | 7/10 — Funciona, código backend agora possui wizards adequados |
| UI/UX (consistência e design) | 20%      | 8/10 — Design system coeso, dark sidebar, animações            |
| Segurança                     | 15%      | 5/10 — Validação server-side fraca, rotas admin públicas       |
| Manutenibilidade              | 10%      | 6/10 — Duplicação de código, typos, manifest incompleto        |
| **Total**                     | **100%** | **~7.5/10**                                                    |

> **Conclusão:** O projecto demonstra uma compreensão sólida da arquitectura Odoo (ORM, QWeb, controllers, assets) e entrega um produto visualmente apelativo com as funcionalidades core do SRS. As principais fragilidades estão na segurança das rotas de administração, na duplicação de código entre as rotas `/portal/*` e as raiz, e na ausência de validação server-side robusta. Para uma versão de produção, estas questões seriam prioritárias.

---

**Segurança e Validação (RNF-03)**

- Implementação recente: foi adicionada validação e sanitização server-side nos controladores para cumprir RNF-03. As mudanças incluem a criação do módulo `custom_addons/crm_estudantil/controllers/validators.py` com helpers (`sanitize_text`, `validate_email`, `sanitize_phone`, `sanitize_choice`, `safe_int`, `safe_id`) e a utilização desses helpers em `main.py` e `gestao.py` para filtrar/validar dados antes de escrever na BD.
- Relatório técnico: veja `docs/RNF-03-report.md` para um resumo das validações aplicadas e instruções de teste.


