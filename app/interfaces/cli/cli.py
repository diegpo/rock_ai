import os, sys, logging, time
from datetime import datetime

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.table import Table
from rich.live import Live
from rich import box

from core.orchestrator import Orchestrator

load_dotenv()

TIMEOUT       = int(os.getenv("ROCKS_TIMEOUT",    "60"))
MAX_INPUT_LEN = int(os.getenv("ROCKS_MAX_INPUT",  "4096"))
VERSION       = os.getenv("ROCKS_VERSION",         "2.1.0")
LOG_FILE      = os.getenv("ROCKS_LOG_FILE",        "rocks_ia.log")

logging.basicConfig(
    filename=LOG_FILE, level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("rocks_ai")

console = Console()
orch    = Orchestrator()
historico: list[dict] = []

ART_TOP = f"""
██████╗  ██████╗  ██████╗██╗  ██╗     █████╗ ██╗   
██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝    ██╔══██╗██║
██████╔╝██║   ██║██║     █████╔╝     ███████║██║   
██╔══██╗██║   ██║██║     ██╔═██╗     ██╔══██║██║   
██║  ██║╚██████╔╝╚██████╗██║  ██╗    ██║  ██║██║ v[bold bright_red]{VERSION}[/bold bright_red]
╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝   
"""

def splash():
    console.clear()
    with Live(console=console, refresh_per_second=20) as live:
        for _ in range(30):
            live.update(Panel(Text.from_markup(ART_TOP), border_style="bold red", padding=(0, 4)))
            time.sleep(0.02)
    console.print("[dim]▸ Carregando core...[/dim]")
    console.print("[dim]▸ Conectando LLM...[/dim]")
    console.print("[bold green]✔ Sistema pronto![/bold green]\n")

def perguntar(mensagem: str) -> str:
    try:
        result = orch.handle(mensagem)
        if isinstance(result, dict):
            return result.get("response") or result.get("message") or str(result)
        return str(result)
    except Exception as e:
        return f"❌ Erro interno: {e}"

AJUDA = """
[bold red]ROCK'S IA CLI[/bold red] — Comandos disponíveis:

  ajuda           → este menu
  hist            → histórico da conversa
  limpar          → limpar histórico
  cls / clear     → limpar tela
  hora            → data/hora atual
  modelo          → ver modelo ativo
  usar ollama     → trocar para Ollama (padrão)
  usar qwen       → trocar para Qwen2.5 (rápido)
  usar gemini     → trocar para Gemini (cloud)
  indexar         → reindexar base de conhecimento Protheus
  sair / exit     → encerrar

[dim]💡 Dica: descreva qualquer erro do Protheus e a IA irá analisar e sugerir solução.[/dim]
"""

def cmd_ajuda():   console.print(Panel(AJUDA, border_style="red"))
def cmd_limpar():  historico.clear(); console.print("[green]✔ Histórico limpo[/green]")
def cmd_modelo():  console.print(f"[cyan]Modelo ativo: {orch.llm.current_model()}[/cyan]")

def cmd_hist():
    if not historico:
        console.print("[dim]Histórico vazio.[/dim]"); return
    t = Table(box=box.SIMPLE)
    t.add_column("N", style="dim", width=4)
    t.add_column("Papel", width=10)
    t.add_column("Mensagem")
    for i, msg in enumerate(historico, 1):
        role = "[red]Você[/red]" if msg["role"] == "user" else "[magenta]IA[/magenta]"
        t.add_row(str(i), role, msg["content"][:120])
    console.print(t)

def cmd_indexar():
    console.print("[dim]📚 Reindexando base de conhecimento...[/dim]")
    try:
        from knowledge.rag_engine import RAGEngine
        rag = RAGEngine()
        n = rag.index_documents()
        console.print(f"[green]✔ {n} chunks indexados com sucesso![/green]")
    except Exception as e:
        console.print(f"[red]❌ Erro ao indexar: {e}[/red]")

COMANDOS = {
    "ajuda":   cmd_ajuda,
    "hist":    cmd_hist,
    "limpar":  cmd_limpar,
    "modelo":  cmd_modelo,
    "indexar": cmd_indexar,
}

def main():
    splash()
    while True:
        try:
            raw = console.input("[bold red]rocks >[/bold red] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n👋 Encerrado"); sys.exit(0)

        if not raw: continue
        cmd = raw.lower()

        if cmd in ("sair", "exit", "quit"):
            console.print("\n👋 Encerrando..."); break

        if cmd in ("cls", "clear"):
            splash(); continue

        if cmd == "hora":
            console.print(f"[red]{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}[/red]")
            continue

        if cmd in COMANDOS:
            COMANDOS[cmd](); continue

        if len(raw) > MAX_INPUT_LEN:
            console.print("[yellow]⚠️ Mensagem muito longa[/yellow]"); continue

        console.print("[dim]⏳ Processando...[/dim]")
        resposta = perguntar(raw)

        historico.append({"role": "user",      "content": raw})
        historico.append({"role": "assistant", "content": resposta})
        log.info(f"USER: {raw[:200]}")
        log.info(f"AI:   {resposta[:200]}")

        try:
            console.print(Panel(Markdown(resposta), title="🤖 ROCK IA", border_style="magenta"))
        except Exception:
            console.print(resposta)
        console.print()

if __name__ == "__main__":
    main()
