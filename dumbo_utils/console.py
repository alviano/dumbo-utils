import logging
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Prompt, Confirm

console = Console()
prompt = Prompt(console=console)
confirm = Confirm(console=console)

logging.basicConfig(
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, markup=True, rich_tracebacks=True)],
)
log = logging.getLogger("rich")
