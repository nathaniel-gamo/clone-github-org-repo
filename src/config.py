import os
import sys
from pathlib import Path

from dotenv import dotenv_values, load_dotenv


def _get_dotenv_path() -> str:

    base_dir: Path
    if getattr(sys, "frozen", False) or getattr(sys, "compiled", False):
        base_dir = Path(sys.executable).parent

    else:
        base_dir = Path(__file__).parent.parent
    
    return str(base_dir / ".env")


def load_config(dotenv_path: str = "", 
                dotenv_only: bool = True) -> dict[str, str | None]:
    
    dotenv_path = (dotenv_path 
                   if (Path(dotenv_path).is_file() 
                       and dotenv_path[-4:] == ".env")
                   else _get_dotenv_path())
    
    if dotenv_only:
        return dotenv_values(dotenv_path)

    load_dotenv(dotenv_path, override=True)

    return {key: value for key, value in os.environ.items()}