#!/usr/bin/env python3
import json
import os
import sys

import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich import box
from rich.text import Text

from prompt import SYSTEM_PROMPT
from tools import TOOL_DEFINITIONS, dispatch_tool

console = Console()

STEP_COLORS = {
    "ARITHMETIC": "cyan",
    "ALGEBRA": "blue",
    "PHYSICS": "green",
    "CHEMISTRY": "yellow",
    "LOGIC": "magenta",
    "LOOKUP": "white",
}


def render_solution(data: dict) -> None:
    steps = data.get("steps", [])
    if steps:
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold white")
        table.add_column("#", style="dim", width=3)
        table.add_column("Type", width=12)
        table.add_column("Reasoning")
        table.add_column("Action", width=14)

        for s in steps:
            tag = s.get("type", "")
            color = STEP_COLORS.get(tag, "white")
            action_str = s.get("action", "")
            if s.get("expression"):
                action_str += f"\n[dim]{s['expression']}[/dim]"
            table.add_row(
                str(s.get("step", "")),
                f"[{color}]{tag}[/{color}]",
                s.get("reasoning", ""),
                action_str,
            )
        console.print(table)

    confidence = data.get("confidence", 0)
    conf_color = "green" if confidence >= 80 else "yellow" if confidence >= 60 else "red"

    console.print(
        Panel(
            f"[bold]{data.get('final_answer', '')}[/bold]\n\n"
            f"[dim]Verification:[/dim] {data.get('verification', '')}\n"
            f"[dim]Confidence:[/dim] [{conf_color}]{confidence}%[/{conf_color}]",
            title="[bold green]Final Answer[/bold green]",
            border_style="green",
        )
    )

    if data.get("follow_up_possible"):
        console.print("[dim]You can ask a follow-up question about this problem.[/dim]\n")


def solve(client: anthropic.Anthropic, history: list[dict], problem: str) -> list[dict]:
    history.append({"role": "user", "content": problem})

    with console.status("[bold cyan]Thinking...[/bold cyan]", spinner="dots"):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOL_DEFINITIONS,
            messages=history,
        )

    while response.stop_reason == "tool_use":
        tool_results = []
        assistant_content = response.content

        for block in response.content:
            if block.type == "tool_use":
                console.print(
                    f"  [dim cyan]→ Calling [bold]{block.name}[/bold]({json.dumps(block.input)})[/dim cyan]"
                )
                result_str = dispatch_tool(block.name, block.input)
                result_data = json.loads(result_str)
                if "error" in result_data:
                    console.print(f"  [red]Tool error:[/red] {result_data['error']}")
                else:
                    console.print(f"  [dim green]← {result_str}[/dim green]")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_str,
                })

        history.append({"role": "assistant", "content": assistant_content})
        history.append({"role": "user", "content": tool_results})

        with console.status("[bold cyan]Continuing reasoning...[/bold cyan]", spinner="dots"):
            response = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=history,
            )

    final_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            final_text = block.text
            break

    history.append({"role": "assistant", "content": response.content})

    try:
        start = final_text.find("{")
        end = final_text.rfind("}") + 1
        data = json.loads(final_text[start:end])
        render_solution(data)
    except (json.JSONDecodeError, ValueError):
        console.print(Panel(final_text, title="Answer", border_style="green"))

    return history


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        console.print("[red]Error:[/red] ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    history: list[dict] = []

    console.print(
        Panel(
            "[bold cyan]EduSolve[/bold cyan] — Multi-Step STEM Problem Solver\n"
            "[dim]Powered by Claude · type [bold]exit[/bold] or [bold]quit[/bold] to stop · [bold]clear[/bold] to reset[/dim]",
            border_style="cyan",
        )
    )

    while True:
        try:
            problem = console.input("\n[bold yellow]Problem:[/bold yellow] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Goodbye.[/dim]")
            break

        if not problem:
            continue
        if problem.lower() in {"exit", "quit"}:
            console.print("[dim]Goodbye.[/dim]")
            break
        if problem.lower() == "clear":
            history = []
            console.print("[dim]Conversation cleared.[/dim]")
            continue

        console.print()
        history = solve(client, history, problem)


if __name__ == "__main__":
    main()
