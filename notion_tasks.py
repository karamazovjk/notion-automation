"""
notion_tasks.py — Resumo semanal de tarefas do Notion no terminal.

Uso:
    python notion_tasks.py

Configuração:
    Copie o arquivo .env.example para .env e preencha com seu token e database ID.
    Veja o README.md para instruções detalhadas.
"""

import os
import sys
from datetime import datetime, date, timedelta
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()

# ── Cores no terminal ────────────────────────────────────────────────────────
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RED    = "\033[91m"
BLUE   = "\033[94m"
GRAY   = "\033[90m"

# ── Mapeamentos ──────────────────────────────────────────────────────────────

# Adapte os valores abaixo para bater com os nomes exatos no seu Notion
STATUS_ORDER = ["Pendente", "Em progresso", "Concluída"]

STATUS_COR = {
    "pendente":     YELLOW,
    "em progresso": CYAN,
    "concluída":    GREEN,
    "concluida":    GREEN,
}

PRIORIDADE_COR = {
    "alta":  RED,
    "média": YELLOW,
    "media": YELLOW,
    "baixa": GRAY,
}

PRIORIDADE_ORDEM = {"alta": 0, "média": 1, "media": 1, "baixa": 2, "": 3}


# ── Helpers ──────────────────────────────────────────────────────────────────

def cor_status(s: str) -> str:
    return STATUS_COR.get(s.lower(), RESET)

def cor_prioridade(p: str) -> str:
    return PRIORIDADE_COR.get(p.lower(), RESET)

def fmt_data(iso: str) -> str:
    """Converte '2024-06-10' em '10/06/2024'."""
    try:
        return date.fromisoformat(iso).strftime("%d/%m/%Y")
    except:
        return iso

def esta_atrasada(prazo_iso: str) -> bool:
    if not prazo_iso:
        return False
    try:
        return date.fromisoformat(prazo_iso) < date.today()
    except:
        return False

def esta_na_semana(prazo_iso: str) -> bool:
    """Retorna True se o prazo é entre hoje e os próximos 7 dias."""
    if not prazo_iso:
        return False
    try:
        d = date.fromisoformat(prazo_iso)
        return date.today() <= d <= date.today() + timedelta(days=7)
    except:
        return False


# ── Leitura do Notion ────────────────────────────────────────────────────────

def buscar_tarefas(client: Client, database_id: str) -> list[dict]:
    """
    Busca todas as tarefas do database e normaliza os campos.
    Retorna uma lista de dicts com: nome, status, prioridade, prazo, categoria.
    """
    try:
        response = client.databases.query(database_id=database_id)
    except Exception as e:
        print(f"\n{RED}  ✗ Erro ao acessar o Notion: {e}{RESET}")
        print(f"{DIM}  Verifique se o token e o database ID estão corretos no .env{RESET}\n")
        sys.exit(1)

    tarefas = []
    for page in response.get("results", []):
        props = page.get("properties", {})

        # ── Nome ──
        nome_prop = props.get("Nome") or props.get("Name") or props.get("Tarefa") or {}
        titulo_list = nome_prop.get("title", [])
        nome = titulo_list[0]["plain_text"] if titulo_list else "(sem nome)"

        # ── Status ──
        status_prop = props.get("Status", {})
        status = ""
        if status_prop.get("type") == "status":
            status = (status_prop.get("status") or {}).get("name", "")
        elif status_prop.get("type") == "select":
            status = (status_prop.get("select") or {}).get("name", "")

        # ── Prioridade ──
        prio_prop = props.get("Prioridade") or props.get("Priority") or {}
        prioridade = (prio_prop.get("select") or {}).get("name", "")

        # ── Prazo ──
        prazo_prop = props.get("Prazo") or props.get("Data") or props.get("Due") or {}
        prazo = ""
        if prazo_prop.get("type") == "date":
            data_obj = prazo_prop.get("date") or {}
            prazo = data_obj.get("start", "")

        # ── Categoria ──
        cat_prop = props.get("Categoria") or props.get("Projeto") or props.get("Category") or {}
        categoria = (cat_prop.get("select") or {}).get("name", "")

        tarefas.append({
            "nome":       nome,
            "status":     status,
            "prioridade": prioridade,
            "prazo":      prazo,
            "categoria":  categoria,
        })

    return tarefas


# ── Exibição ─────────────────────────────────────────────────────────────────

def exibir_tarefa(t: dict, indice: int):
    """Imprime uma linha de tarefa formatada."""
    # ícone de prioridade
    icones = {"alta": "🔴", "média": "🟡", "media": "🟡", "baixa": "🔵"}
    icone = icones.get(t["prioridade"].lower(), "⚪")

    # prazo formatado
    prazo_str = ""
    if t["prazo"]:
        if esta_atrasada(t["prazo"]):
            prazo_str = f"  {RED}⚠ atrasada ({fmt_data(t['prazo'])}){RESET}"
        elif esta_na_semana(t["prazo"]):
            prazo_str = f"  {YELLOW}📅 {fmt_data(t['prazo'])}{RESET}"
        else:
            prazo_str = f"  {GRAY}📅 {fmt_data(t['prazo'])}{RESET}"

    # categoria
    cat_str = f"  {GRAY}[{t['categoria']}]{RESET}" if t["categoria"] else ""

    # prioridade
    prio_str = ""
    if t["prioridade"]:
        c = cor_prioridade(t["prioridade"])
        prio_str = f"  {c}{t['prioridade'].upper()}{RESET}"

    print(f"  {icone} {BOLD}{t['nome']}{RESET}{prio_str}{cat_str}{prazo_str}")


def exibir_resumo(tarefas: list[dict]):
    """Monta e imprime o resumo completo no terminal."""
    hoje = date.today().strftime("%d/%m/%Y")
    semana_fim = (date.today() + timedelta(days=7)).strftime("%d/%m/%Y")

    # ── Cabeçalho ──
    print(f"\n{BOLD}{CYAN}{'═'*54}{RESET}")
    print(f"{BOLD}{CYAN}  📋  TAREFAS DA SEMANA{RESET}")
    print(f"{CYAN}  {hoje}  →  {semana_fim}{RESET}")
    print(f"{BOLD}{CYAN}{'═'*54}{RESET}\n")

    if not tarefas:
        print(f"  {GRAY}Nenhuma tarefa encontrada no database.{RESET}\n")
        return

    # ── Agrupa por status, na ordem definida ──
    grupos: dict[str, list[dict]] = {}
    for s in STATUS_ORDER:
        grupos[s] = []
    grupos["Outros"] = []

    for t in tarefas:
        chave = next((s for s in STATUS_ORDER if s.lower() == t["status"].lower()), "Outros")
        grupos[chave].append(t)

    # dentro de cada grupo, prioridade alta primeiro
    for chave in grupos:
        grupos[chave].sort(
            key=lambda t: PRIORIDADE_ORDEM.get(t["prioridade"].lower(), 3)
        )

    # ── Exibe cada grupo ──
    total_exibido = 0
    for status in [*STATUS_ORDER, "Outros"]:
        lista = grupos[status]
        if not lista:
            continue

        cor = cor_status(status)
        print(f"{BOLD}{cor}  ▸ {status.upper()}  ({len(lista)}){RESET}")
        print(f"{GRAY}  {'─'*46}{RESET}")

        for t in lista:
            exibir_tarefa(t, total_exibido)
            total_exibido += 1
        print()

    # ── Rodapé com contagens ──
    print(f"{BOLD}{CYAN}{'─'*54}{RESET}")
    pendentes   = len(grupos.get("Pendente", []))
    em_prog     = len(grupos.get("Em progresso", []))
    concluidas  = len(grupos.get("Concluída", []))
    atrasadas   = sum(1 for t in tarefas if esta_atrasada(t["prazo"]))
    alta_prio   = sum(1 for t in tarefas if t["prioridade"].lower() == "alta"
                      and t["status"].lower() != "concluída")

    print(f"  {GRAY}Total: {len(tarefas)}  │  "
          f"{YELLOW}Pendentes: {pendentes}  │  "
          f"{CYAN}Em progresso: {em_prog}  │  "
          f"{GREEN}Concluídas: {concluidas}{RESET}")

    if atrasadas:
        print(f"  {RED}⚠  {atrasadas} tarefa(s) com prazo vencido!{RESET}")
    if alta_prio:
        print(f"  {RED}🔴  {alta_prio} tarefa(s) de alta prioridade em aberto{RESET}")

    print(f"{BOLD}{CYAN}{'═'*54}{RESET}\n")


# ── Entry point ──────────────────────────────────────────────────────────────

def main():
    token       = os.getenv("NOTION_TOKEN")
    database_id = os.getenv("NOTION_DATABASE_ID")

    if not token or not database_id:
        print(f"\n{RED}  ✗ Variáveis de ambiente não encontradas.{RESET}")
        print(f"{DIM}  Crie um arquivo .env baseado no .env.example e preencha os valores.{RESET}")
        print(f"{DIM}  Veja o README.md para instruções.{RESET}\n")
        sys.exit(1)

    client  = Client(auth=token)
    tarefas = buscar_tarefas(client, database_id)
    exibir_resumo(tarefas)


if __name__ == "__main__":
    main()
