"""Rich TUI: Status, Input, Feedback."""
from __future__ import annotations

import sys
from typing import Callable

from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class TUI:
    """TUI für Live-Betrieb: Profil, BPM, Parameter, letzte Phrase, scheduled actions."""

    def __init__(self):
        self.console = Console()
        self._state: dict = {}
        self._last_phrase = ""
        self._last_intent = ""
        self._last_confidence = 0.0
        self._last_method = ""
        self._scheduled: list[str] = []
        self._active_macro = ""
        self._message = ""
        self._waiting_confirm = False

    def update_state(self, state: dict) -> None:
        self._state = dict(state)

    def update_result(self, phrase: str, intent: str, confidence: float, method: str) -> None:
        self._last_phrase = phrase
        self._last_intent = intent
        self._last_confidence = confidence
        self._last_method = method

    def update_scheduled(self, items: list[str]) -> None:
        self._scheduled = items

    def update_active_macro(self, name: str) -> None:
        self._active_macro = name

    def set_message(self, msg: str) -> None:
        self._message = msg

    def set_waiting_confirm(self, waiting: bool) -> None:
        self._waiting_confirm = waiting

    def _make_layout(self) -> Layout:
        layout = Layout()

        # Status-Tabelle
        status = Table(show_header=False)
        status.add_column(style="cyan")
        status.add_column(style="green")
        state = self._state
        status.add_row("Profil", str(state.get("profile", "-")))
        status.add_row("BPM", str(state.get("bpm", 128)))
        status.add_row("Energy", f"{state.get('energy', 0.5):.2f}")
        status.add_row("Darkness", f"{state.get('darkness', 0.5):.2f}")
        status.add_row("Hats", f"{state.get('hats', 0.5):.2f}")
        status.add_row("Kick", "ON" if state.get("kick_on", 1) else "OFF")

        layout.split_column(
            Layout(Panel(status, title="[bold]Status[/]"), name="status"),
            Layout(
                Panel(
                    Text.from_markup(
                        f"Phrase: [yellow]{self._last_phrase or '-'}[/]\n"
                        f"Intent: [green]{self._last_intent or '-'}[/] "
                        f"(conf: {self._last_confidence:.2f}) [{self._last_method}]"
                    ),
                    title="[bold]Letzter Befehl[/]",
                ),
                name="last",
            ),
            Layout(
                Panel(
                    "\n".join(self._scheduled) if self._scheduled else "-",
                    title="[bold]Geplant[/]",
                ),
                name="scheduled",
            ),
            Layout(
                Panel(
                    self._active_macro or "-",
                    title="[bold]Aktives Makro[/]",
                ),
                name="macro",
            ),
        )
        if self._message or self._waiting_confirm:
            layout.split_column(
                layout,
                Layout(
                    Panel(
                        (self._message or "Unsicher. Sag: ja / nein / abbrechen") + (
                            " [dim][Warte auf Bestätigung...][/]" if self._waiting_confirm else ""
                        ),
                        title="[bold]Hinweis[/]",
                        style="yellow",
                    ),
                    name="msg",
                ),
            )
        return layout

    def render(self) -> None:
        self.console.print(self._make_layout())

    def print_help(self) -> None:
        self.console.print("[bold]Tasten:[/] Enter = aufnehmen | d = Geräte | m = Makros | p = Profile | q = Beenden")

    def print_devices(self, devices: list) -> None:
        table = Table(title="Audiogeräte")
        table.add_column("Index", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Channels In")
        table.add_column("Sample Rate")
        for d in devices:
            if "error" in d:
                table.add_row("-", str(d["error"]), "-", "-")
            else:
                table.add_row(str(d["index"]), d["name"], str(d["channels_in"]), str(d["sample_rate"]))
        self.console.print(table)


def run_tui(
    on_enter: Callable[[], None],
    on_key: Callable[[str], None],
    get_state: Callable[[], dict],
    get_last_result: Callable[[], tuple],
    get_scheduled: Callable[[], list],
    get_active_macro: Callable[[], str],
    get_message: Callable[[], str],
    get_waiting_confirm: Callable[[], bool],
    list_devices: Callable[[], list],
) -> None:
    """Blocking TUI-Loop. Enter=aufnehmen, d=devices, q=quit, m=macros, p=profiles."""
    tui = TUI()

    def refresh():
        tui.update_state(get_state())
        phr, intent, conf, method = get_last_result()
        tui.update_result(phr or "", intent or "", conf or 0, method or "")
        tui.update_scheduled(get_scheduled())
        tui.update_active_macro(get_active_macro() or "")
        tui.set_message(get_message() or "")
        tui.set_waiting_confirm(get_waiting_confirm())
        tui.render()
        tui.print_help()

    has_tty = False
    try:
        import select
        import tty
        import termios
        has_tty = sys.stdin.isatty()
    except (ImportError, OSError):
        pass

    if has_tty:
        try:
            old_settings = termios.tcgetattr(sys.stdin)
        except (OSError, AttributeError):
            has_tty = False

    if has_tty:
        try:
            tty.setcbreak(sys.stdin.fileno())
            refresh()
            while True:
                if select.select([sys.stdin], [], [], 0.5)[0]:
                    ch = sys.stdin.read(1)
                    if ch == "\n" or ch == "\r":
                        on_enter()
                    elif ch == "q":
                        break
                    elif ch == "d":
                        tui.print_devices(list_devices())
                    elif ch == "m":
                        from svc.macros.registry import list_macros
                        tui.console.print("[bold]Makros:[/]", list_macros())
                    elif ch == "p":
                        from svc.profiles.profiles import list_profiles
                        tui.console.print("[bold]Profile:[/]", list_profiles())
                    else:
                        on_key(ch)
                    refresh()
        except Exception:
            has_tty = False
        finally:
            if has_tty:
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                except Exception:
                    pass

    if not has_tty:
        # Fallback: Einfacher input()-Loop ohne TTY
        tui.console.print("[yellow]Kein TTY – nutze einfachen Input-Modus. q zum Beenden.[/]")
        refresh()
        while True:
            try:
                line = input("> ").strip().lower()
            except EOFError:
                break
            if line == "q":
                break
            if line in ("", "enter", "record"):
                on_enter()
            elif line == "d":
                tui.print_devices(list_devices())
            elif line == "m":
                from svc.macros.registry import list_macros
                tui.console.print("[bold]Makros:[/]", list_macros())
            elif line == "p":
                from svc.profiles.profiles import list_profiles
                tui.console.print("[bold]Profile:[/]", list_profiles())
            refresh()
