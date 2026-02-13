"""
UI Module for AI Assistant using Rich library
Provides beautiful console output with panels, syntax highlighting, and status updates
"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.live import Live
from rich.table import Table
from rich.prompt import Prompt
from rich.status import Status
from rich.layout import Layout
from rich import box
from rich.text import Text
import time


class AssistantUI:
    """Beautiful UI for the AI Assistant using Rich library"""

    def __init__(self):
        self.console = Console()

    def show_welcome(self):
        """Display welcome banner"""
        welcome_text = """
# 🤖 AI Assistant
        
Welcome to your AI-powered file assistant!

**Available Commands:**
- Type your message to interact with the AI
- Use `@filename` to insert file contents into your prompts
- Type `/model` to switch between AI models
- Type `quit`, `exit`, or `q` to exit
        """
        self.console.print(
            Panel(
                Markdown(welcome_text),
                title="[bold cyan]Welcome[/bold cyan]",
                border_style="cyan",
                box=box.DOUBLE,
            )
        )
        self.console.print()

    def show_separator(self, char="─", style="dim"):
        """Show a separator line"""
        self.console.print(char * self.console.width, style=style)

    def get_user_input(self) -> str:
        """Get user input with nice formatting"""
        return Prompt.ask("\n[bold green]You[/bold green]")

    def show_user_message(self, message: str):
        """Display user message"""
        self.console.print(
            Panel(
                message,
                title="[bold green]You[/bold green]",
                border_style="green",
                box=box.ROUNDED,
            )
        )

    def show_ai_message(self, message: str):
        """Display AI response"""
        self.console.print(
            Panel(
                Markdown(message) if message else "[dim]No response[/dim]",
                title="[bold blue]AI Assistant[/bold blue]",
                border_style="blue",
                box=box.ROUNDED,
            )
        )

    def show_tool_call(self, tool_name: str, args: dict = None):
        """Display tool being called"""
        args_text = ""
        if args:
            args_formatted = "\n".join([f"  • {k}: {v}" for k, v in args.items()])
            args_text = f"\n\n[dim]Parameters:[/dim]\n{args_formatted}"

        self.console.print(
            Panel(
                f"[bold yellow]🔧 {tool_name}[/bold yellow]{args_text}",
                title="[bold yellow]Tool Call[/bold yellow]",
                border_style="yellow",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )

    def show_tool_result(self, result: str):
        """Display tool execution result"""
        self.console.print(
            Panel(
                f"[green]✓[/green] {result}",
                title="[bold green]Result[/bold green]",
                border_style="green",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )

    def show_diff(self, diff: str, max_lines: int = 10):
        """
        Display a diff with syntax highlighting, truncating if too long.

        Args:
            diff (str): The diff content to display
            max_lines (int): Maximum number of lines to show before truncating
        """
        if not diff:
            return

        diff_lines = diff.splitlines()
        total_lines = len(diff_lines)

        if total_lines > max_lines:
            # Truncate and add indicator
            displayed_diff = "\n".join(diff_lines[:max_lines])
            displayed_diff += f"\n\n... ({total_lines - max_lines} more lines omitted)"
            truncated = True
        else:
            displayed_diff = diff
            truncated = False

        # Use Syntax for diff highlighting
        syntax = Syntax(displayed_diff, "diff", theme="monokai", line_numbers=False)

        title = "[bold magenta]📝 Diff"
        if truncated:
            title += f" (showing {max_lines}/{total_lines} lines)"
        title += "[/bold magenta]"

        self.console.print(
            Panel(
                syntax,
                title=title,
                border_style="magenta",
                box=box.ROUNDED,
                padding=(0, 1),
            )
        )

    def show_error(self, error: str):
        """Display error message"""
        self.console.print(
            Panel(
                f"[bold red]✗[/bold red] {error}",
                title="[bold red]Error[/bold red]",
                border_style="red",
                box=box.HEAVY,
            )
        )

    def show_info(self, message: str):
        """Display info message"""
        self.console.print(f"[dim cyan]ℹ {message}[/dim cyan]")

    def show_thinking(self):
        """Show a thinking status"""
        return Status(
            "[bold cyan]🤔 AI is thinking...[/bold cyan]", console=self.console
        )

    def show_processing(self, message: str = "Processing..."):
        """Show a processing status"""
        return Status(f"[bold yellow]⚙️  {message}[/bold yellow]", console=self.console)

    def show_goodbye(self):
        """Display goodbye message"""
        self.console.print("\n")
        self.console.print(
            Panel(
                "[bold cyan]👋 Thank you for using AI Assistant!\n\nGoodbye![/bold cyan]",
                border_style="cyan",
                box=box.DOUBLE,
            )
        )

    def show_file_content(self, filename: str, content: str, language: str = "python"):
        """Display file content with syntax highlighting"""
        syntax = Syntax(content, language, theme="monokai", line_numbers=True)
        self.console.print(
            Panel(
                syntax,
                title=f"[bold magenta]📄 {filename}[/bold magenta]",
                border_style="magenta",
                box=box.ROUNDED,
            )
        )

    def show_model_info(self, model: str):
        """Display current model information"""
        self.console.print(f"[dim]Using model: {model}[/dim]\n")

    def show_model_selector(self, models: list, current_model: str) -> str:
        """Display model selection menu and return selected model"""
        # Create a table showing available models
        table = Table(
            title="🤖 Available AI Models", box=box.ROUNDED, border_style="cyan"
        )
        table.add_column("Number", style="cyan", justify="center")
        table.add_column("Model", style="green")
        table.add_column("Status", style="yellow")

        for idx, model in enumerate(models, 1):
            status = "✓ Current" if model == current_model else ""
            table.add_row(str(idx), model, status)

        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n")

        # Get user selection
        while True:
            try:
                choice = Prompt.ask(
                    "[bold cyan]Select model number[/bold cyan]",
                    choices=[str(i) for i in range(1, len(models) + 1)],
                )
                selected_model = models[int(choice) - 1]

                # Confirm selection
                self.console.print(
                    Panel(
                        f"✓ Model switched to: [bold green]{selected_model}[/bold green]",
                        border_style="green",
                        box=box.ROUNDED,
                    )
                )

                return selected_model
            except (ValueError, IndexError):
                self.show_error("Invalid selection. Please try again.")

    def clear_screen(self):
        """Clear the console screen"""
        self.console.clear()

    def create_stats_table(self, stats: dict) -> Table:
        """Create a statistics table"""
        table = Table(title="Session Statistics", box=box.SIMPLE)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in stats.items():
            table.add_row(key, str(value))

        return table

    def show_stats(self, stats: dict):
        """Display statistics"""
        self.console.print(self.create_stats_table(stats))
