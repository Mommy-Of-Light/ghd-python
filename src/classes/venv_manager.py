#!/usr/bin/env python3
import sys
import os
import platform
import venv
from pathlib import Path

def ensure_isolated_venv(venv_dir: Path):
    """
    Create an isolated virtual environment if it doesn't exist
    and re-launch the script inside it.
    """
    venv_dir = Path(venv_dir)
    if not venv_dir.exists():
        print(f"Creating isolated environment at {venv_dir}")
        venv.create(str(venv_dir), with_pip=True)

    # Determine python executable inside venv
    py_exe = venv_dir / ("Scripts/python.exe" if platform.system() == "Windows" else "bin/python")
    if not py_exe.exists():
        print("Python executable not found in venv")
        return

    # Check if we're already running inside this venv
    curr = Path(sys.executable).resolve()
    if curr == py_exe.resolve():
        return

    # Relaunch the script using the venv python
    os.execv(str(py_exe), [str(py_exe), str(Path(__file__).resolve())] + sys.argv[1:])
