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
- Type `quit`, `exit`, or `q` to exit
        """
        self.console.print(Panel(
            Markdown(welcome_text),
            title="[bold cyan]Welcome[/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE
        ))
        self.console.print()
        
    def show_separator(self, char="─", style="dim"):
        """Show a separator line"""
        self.console.print(char * self.console.width, style=style)
        
    def get_user_input(self) -> str:
        """Get user input with nice formatting"""
        return Prompt.ask("\n[bold green]You[/bold green]")
        
    def show_user_message(self, message: str):
        """Display user message"""
        self.console.print(Panel(
            message,
            title="[bold green]You[/bold green]",
            border_style="green",
            box=box.ROUNDED
        ))
        
    def show_ai_message(self, message: str):
        """Display AI response"""
        self.console.print(Panel(
            Markdown(message) if message else "[dim]No response[/dim]",
            title="[bold blue]AI Assistant[/bold blue]",
            border_style="blue",
            box=box.ROUNDED
        ))
        
    def show_tool_call(self, tool_name: str, args: dict = None):
        """Display tool being called"""
        args_text = ""
        if args:
            args_formatted = "\n".join([f"  • {k}: {v}" for k, v in args.items()])
            args_text = f"\n\n[dim]Parameters:[/dim]\n{args_formatted}"
            
        self.console.print(Panel(
            f"[bold yellow]🔧 {tool_name}[/bold yellow]{args_text}",
            title="[bold yellow]Tool Call[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(0, 1)
        ))
        
    def show_tool_result(self, result: str):
        """Display tool execution result"""
        self.console.print(Panel(
            f"[green]✓[/green] {result}",
            title="[bold green]Result[/bold green]",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1)
        ))
        
    def show_error(self, error: str):
        """Display error message"""
        self.console.print(Panel(
            f"[bold red]✗[/bold red] {error}",
            title="[bold red]Error[/bold red]",
            border_style="red",
            box=box.HEAVY
        ))
        
    def show_info(self, message: str):
        """Display info message"""
        self.console.print(f"[dim cyan]ℹ {message}[/dim cyan]")
        
    def show_thinking(self):
        """Show a thinking status"""
        return Status("[bold cyan]🤔 AI is thinking...[/bold cyan]", console=self.console)
        
    def show_processing(self, message: str = "Processing..."):
        """Show a processing status"""
        return Status(f"[bold yellow]⚙️  {message}[/bold yellow]", console=self.console)
        
    def show_goodbye(self):
        """Display goodbye message"""
        self.console.print("\n")
        self.console.print(Panel(
            "[bold cyan]👋 Thank you for using AI Assistant!\n\nGoodbye![/bold cyan]",
            border_style="cyan",
            box=box.DOUBLE
        ))
        
    def show_file_content(self, filename: str, content: str, language: str = "python"):
        """Display file content with syntax highlighting"""
        syntax = Syntax(content, language, theme="monokai", line_numbers=True)
        self.console.print(Panel(
            syntax,
            title=f"[bold magenta]📄 {filename}[/bold magenta]",
            border_style="magenta",
            box=box.ROUNDED
        ))
        
    def show_model_info(self, model: str):
        """Display current model information"""
        self.console.print(f"[dim]Using model: {model}[/dim]\n")
        
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
