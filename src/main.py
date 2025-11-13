#!/usr/bin/env python3
from classes.cli import FileManagerCLI
from classes.venv_manager import ensure_isolated_venv
from pathlib import Path
import sys

def main():
    if "--isolated" in sys.argv:
        ensure_isolated_venv(Path(".venv"))
    cli = FileManagerCLI()
    cli.run()

if __name__ == "__main__":
    main()
