# Notion Weekly Tasks

Script Python que lê um database do Notion e exibe um resumo semanal de tarefas direto no terminal — agrupado por status, com prioridade alta em destaque.

Além de rodar como .bat, planejo fazer essa funcionalidade como um PyInstaller em um futuro próximo.

---

## Como fica no terminal

```
══════════════════════════════════════════════════════
  📋  TAREFAS DA SEMANA
  10/06/2024  →  17/06/2024
══════════════════════════════════════════════════════

  ▸ EM PROGRESSO  (2)
  ──────────────────────────────────────────────────
  🔴 Entregar relatório  ALTA  [Faculdade]  📅 12/06/2024
  🟡 Revisar código do projeto  MÉDIA  [Trabalho]

  ▸ PENDENTE  (3)
  ──────────────────────────────────────────────────
  🔴 Estudar para prova  ALTA  [Faculdade]  ⚠ atrasada (08/06/2024)
  🟡 Responder emails  MÉDIA
  🔵 Organizar desktop  BAIXA  [Pessoal]

──────────────────────────────────────────────────────
  Total: 5  │  Pendentes: 3  │  Em progresso: 2  │  Concluídas: 0
  ⚠  1 tarefa(s) com prazo vencido!
  🔴  3 tarefa(s) de alta prioridade em aberto
══════════════════════════════════════════════════════
```

---

## Configuração (5 minutos)

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/notion-weekly-tasks.git
cd notion-weekly-tasks
```

### 2. Instale as dependências
```bash
pip install -r requirements.txt
```

### 3. Crie uma integração no Notion

1. Acesse [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Clique em **New integration**
3. Dê um nome (ex: `weekly-tasks`) e salve
4. Copie o **Internal Integration Secret** (começa com `secret_`)

### 4. Crie o database de tarefas no Notion

Crie um database com as seguintes colunas:

| Coluna | Tipo | Opções sugeridas |
|---|---|---|
| Nome | Title | — |
| Status | Status | Pendente, Em progresso, Concluída |
| Prioridade | Select | Alta, Média, Baixa |
| Prazo | Date | — |
| Categoria | Select | Trabalho, Faculdade, Pessoal... |

> Se você já tem um database, basta garantir que as colunas existam com esses nomes.

### 5. Conecte a integração ao database

1. Abra o database no Notion
2. Clique nos `...` (canto superior direito) → **Connections** → adicione sua integração

### 6. Pegue o ID do database

Abra o database no navegador. A URL tem este formato:
```
https://notion.so/seu-workspace/XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX?v=...
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                        esse é o ID
```

### 7. Configure o arquivo .env

```bash
cp .env.example .env
```

Edite o `.env` com seu token e database ID:
```
NOTION_TOKEN=secret_...
NOTION_DATABASE_ID=...
```

### 8. Execute
```bash
python notion_tasks.py
```

---

## Tecnologias

- **Python 3.10+**
- [`notion-client`](https://github.com/ramnes/notion-sdk-py) — SDK oficial do Notion
- [`python-dotenv`](https://github.com/theskumar/python-dotenv) — leitura de variáveis de ambiente

---

## Aprendizados

- Consumo de API REST com SDK oficial
- Leitura e normalização de dados semi-estruturados (propriedades do Notion)
- Organização de projeto Python simples e reutilizável
- Boas práticas de segurança com `.env` e `.gitignore`

---

> Projeto desenvolvido para fins de aprendizado e uso pessoal.
