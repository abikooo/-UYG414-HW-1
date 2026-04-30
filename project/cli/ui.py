from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.align import Align
from rich import box

console = Console()

# ── Color Palette (Inspired by Claude Code / Gemini CLI) ──
ACCENT = "#a78bfa"       # Soft purple
ACCENT_DIM = "#7c3aed"   # Deep purple
SUCCESS = "#34d399"       # Mint green
ERROR = "#f87171"         # Soft red
WARNING = "#fbbf24"       # Amber
INFO = "#60a5fa"          # Sky blue
DIM = "#6b7280"           # Gray
SURFACE = "#1e1b2e"       # Dark surface
BORDER = "#4c1d95"        # Purple border


LOGO = r"""
[bold #a78bfa]  ╦  ╔═╗╔═╗  ╦╔╗╔╔╦╗╔═╗╦  ╦  ╦╔═╗╔═╗╔╗╔╔═╗╔═╗[/]
[bold #8b5cf6]  ║  ║ ║║ ╦  ║║║║ ║ ║╣ ║  ║  ║║ ╦║╣ ║║║║  ║╣ [/]
[bold #7c3aed]  ╩═╝╚═╝╚═╝  ╩╝╚╝ ╩ ╚═╝╩═╝╩═╝╩╚═╝╚═╝╝╚╝╚═╝╚═╝[/]
[dim #6b7280]  AI-Powered Security Operations Platform • v1.0[/]
"""


def print_banner():
    """Print the application banner."""
    console.print()
    console.print(
        Panel(
            Align.center(Text.from_markup(LOGO)),
            border_style=ACCENT_DIM,
            box=box.DOUBLE_EDGE,
            padding=(0, 2),
        )
    )
    console.print()


def print_menu(options: list[dict]):
    """Print an interactive menu."""
    table = Table(
        show_header=False,
        box=None,
        padding=(0, 2),
        expand=False,
    )
    table.add_column("key", style=f"bold {ACCENT}", width=4)
    table.add_column("label", style="white")
    table.add_column("desc", style=f"{DIM}")

    for opt in options:
        table.add_row(opt["key"], opt["label"], opt.get("desc", ""))

    console.print(
        Panel(
            table,
            title=f"[bold {ACCENT}]  Menu[/]",
            border_style=ACCENT_DIM,
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )


def print_success(message: str):
    console.print(f"  [{SUCCESS}]✓[/] {message}")


def print_error(message: str):
    console.print(f"  [{ERROR}]✗[/] {message}")


def print_warning(message: str):
    console.print(f"  [{WARNING}]⚠[/] {message}")


def print_info(message: str):
    console.print(f"  [{INFO}]ℹ[/] {message}")


def print_section(title: str):
    console.print()
    console.print(f"  [bold {ACCENT}]▸ {title}[/]")
    console.print(f"  [{DIM}]{'─' * 50}[/]")


def print_kv(key: str, value: str, indent: int = 4):
    pad = " " * indent
    console.print(f"{pad}[{DIM}]{key}:[/] [white]{value}[/]")


def print_log_entry(log: dict):
    """Pretty-print a single log entry."""
    level = log.get("level", "INFO").upper()
    level_colors = {
        "DEBUG": DIM,
        "INFO": INFO,
        "WARNING": WARNING,
        "ERROR": ERROR,
        "CRITICAL": "#dc2626",
    }
    color = level_colors.get(level, DIM)

    ts = log.get("timestamp", log.get("created_at", ""))[:19]
    svc = log.get("service_name", "—")
    msg = log.get("message", "")
    classification = log.get("ai_classification", "")

    line = f"  [{DIM}]{ts}[/]  [{color}]{level:8s}[/]  [{DIM}]{svc:15s}[/]  [white]{msg}[/]"
    if classification:
        line += f"  [bold {ACCENT}][{classification}][/]"
    console.print(line)


def print_logs_table(logs: list[dict]):
    """Print logs in a styled table."""
    if not logs:
        print_warning("No logs found.")
        return

    table = Table(
        box=box.SIMPLE_HEAD,
        border_style=ACCENT_DIM,
        header_style=f"bold {ACCENT}",
        padding=(0, 1),
        expand=True,
    )
    table.add_column("Timestamp", style=DIM, width=20)
    table.add_column("Level", width=10)
    table.add_column("Service", style=DIM, width=16)
    table.add_column("Message", ratio=1)
    table.add_column("AI Tag", style=f"bold {ACCENT}", width=18)

    level_colors = {
        "DEBUG": DIM, "INFO": INFO, "WARNING": WARNING,
        "ERROR": ERROR, "CRITICAL": "#dc2626",
    }

    for log in logs:
        level = log.get("level", "INFO").upper()
        color = level_colors.get(level, DIM)
        ts = log.get("timestamp", log.get("created_at", ""))[:19]

        table.add_row(
            ts,
            f"[{color}]{level}[/]",
            log.get("service_name", "—"),
            log.get("message", "")[:80],
            log.get("ai_classification", "—"),
        )

    console.print()
    console.print(table)


def print_health_status(services: dict):
    """Print health status for all services."""
    table = Table(
        box=box.ROUNDED,
        border_style=ACCENT_DIM,
        header_style=f"bold {ACCENT}",
        padding=(0, 2),
        title=f"[bold {ACCENT}]  System Health[/]",
    )
    table.add_column("Service", style="white", width=22)
    table.add_column("Status", width=14)
    table.add_column("Details", style=DIM)

    for name, data in services.items():
        status = data.get("status", "unknown")
        if status == "healthy":
            status_display = f"[{SUCCESS}]● healthy[/]"
        elif status == "degraded":
            status_display = f"[{WARNING}]◐ degraded[/]"
        else:
            status_display = f"[{ERROR}]○ offline[/]"

        detail = data.get("database", data.get("error", "—"))
        table.add_row(name, status_display, str(detail)[:40])

    console.print()
    console.print(table)
    console.print()


def print_ai_result(title: str, result: dict):
    """Print AI analysis result in a styled panel."""
    body = result.get("summary", result.get("anomalies", "No data."))
    latency = result.get("latency_ms", 0)
    tokens = result.get("tokens", 0)

    footer = f"[{DIM}]latency: {latency}ms  •  tokens: {tokens}[/]"

    console.print()
    console.print(
        Panel(
            f"[white]{body}[/]\n\n{footer}",
            title=f"[bold {ACCENT}] {title}[/]",
            border_style=ACCENT_DIM,
            box=box.ROUNDED,
            padding=(1, 2),
            expand=True,
        )
    )
    console.print()


def print_metrics(data: dict):
    """Print system metrics."""
    table = Table(
        box=box.ROUNDED,
        border_style=ACCENT_DIM,
        header_style=f"bold {ACCENT}",
        padding=(0, 2),
        title=f"[bold {ACCENT}] 📊 System Metrics[/]",
    )
    table.add_column("Metric", style="white", width=35)
    table.add_column("Value", style=f"bold {SUCCESS}", width=20)

    table.add_row("Total Logs Ingested", str(data.get("total_logs_ingested", 0)))
    table.add_row("AI Calls Today", str(data.get("ai_calls_today", 0)))
    table.add_row("Avg AI Latency (ms)", str(data.get("avg_ai_classification_latency_ms", 0)))

    by_level = data.get("logs_by_level", {})
    for level, count in by_level.items():
        table.add_row(f"  └─ {level}", str(count))

    console.print()
    console.print(table)
    console.print()


def prompt(label: str, password: bool = False) -> str:
    """Styled input prompt."""
    return console.input(f"  [{ACCENT}]▸[/] [white]{label}:[/] ")
