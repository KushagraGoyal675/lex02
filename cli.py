import os
import sys
import json
import logging
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger("rich")
console = Console()

class CourtroomCLI:
    def __init__(self):
        self.console = Console()
        self.session_id = None
        self.case_data = None
        self.simulation = None

    def print_header(self):
        """Print the application header"""
        self.console.print(Panel.fit(
            "[bold red]Indian Court Simulator[/bold red]\n"
            "[bold]Interactive Courtroom Simulation[/bold]",
            border_style="red"
        ))

    def print_case_info(self, case_data):
        """Print case information"""
        table = Table(title="Case Information", border_style="red")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Case ID", case_data.get('case_id', 'N/A'))
        table.add_row("Title", case_data.get('title', 'N/A'))
        table.add_row("Type", case_data.get('case_type', 'N/A'))
        table.add_row("Plaintiff", case_data.get('parties', {}).get('plaintiff', 'N/A'))
        table.add_row("Defendant", case_data.get('parties', {}).get('defendant', 'N/A'))

        self.console.print(table)

    def print_llm_output(self, role, content):
        """Print LLM output with role and content"""
        self.console.print(Panel(
            f"[bold]{role}:[/bold]\n{content}",
            title="LLM Output",
            border_style="red"
        ))

    def print_event(self, event_type, data):
        """Print event information"""
        self.console.print(Panel(
            f"[bold]{event_type}[/bold]\n{json.dumps(data, indent=2)}",
            title="Event",
            border_style="blue"
        ))

    def print_error(self, error):
        """Print error message"""
        self.console.print(Panel(
            f"[bold red]Error:[/bold red] {error}",
            title="Error",
            border_style="red"
        ))

    def print_status(self, status):
        """Print status message"""
        self.console.print(Panel(
            status,
            title="Status",
            border_style="green"
        ))

    def start_simulation(self, case_data):
        """Start a new simulation"""
        self.case_data = case_data
        self.print_header()
        self.print_case_info(case_data)
        self.print_status("Starting simulation...")

    def update_state(self, state):
        """Update and print simulation state"""
        if 'transcript' in state:
            for entry in state['transcript']:
                self.print_llm_output(entry['speaker'], entry['content'])

        if 'animation' in state:
            self.print_status("Animation updated")

        if 'evidence_presented' in state:
            for evidence in state['evidence_presented']:
                self.print_event("Evidence Presented", evidence)

        if 'objections' in state:
            for objection in state['objections']:
                self.print_event("Objection", objection)

    def end_simulation(self):
        """End the simulation"""
        self.print_status("Simulation ended")
        self.console.print("\nThank you for using Indian Court Simulator!")

def main():
    cli = CourtroomCLI()
    
    # Example usage
    case_data = {
        "case_id": "test_case_1",
        "title": "Test Case",
        "case_type": "Civil",
        "parties": {
            "plaintiff": "Test Plaintiff",
            "defendant": "Test Defendant"
        }
    }
    
    cli.start_simulation(case_data)
    
    # Example state update
    state = {
        "transcript": [
            {
                "speaker": "Judge",
                "content": "Court is now in session.",
                "timestamp": datetime.now().isoformat()
            }
        ],
        "animation": "<svg>...</svg>",
        "evidence_presented": [],
        "objections": []
    }
    
    cli.update_state(state)
    cli.end_simulation()

if __name__ == "__main__":
    main() 