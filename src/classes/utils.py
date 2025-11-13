#!/usr/bin/env python3
import os
from pathlib import Path
import stat, datetime

HISTFILE = Path.home() / ".pyhist"

def make_abs_path(p: str, workspace: Path = Path("/home/user")) -> Path:
    path = Path(p).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve()
    try:
        path.relative_to(workspace)
    except ValueError:
        print("Access denied: path outside workspace")
        return workspace
    return path

def human_size(n):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"

def pager_lines(lines, lines_per_page=25):
    i = 0
    n = len(lines)
    while i < n:
        end = min(i + lines_per_page, n)
        for idx, line in enumerate(lines[i:end], start=i+1):
            print(f"{idx:4}: {line}", end="")
        i = end
        if i >= n:
            break
        c = input("--More-- (Enter=1 line, Space=page, q=quit) ")
        if c == "q":
            break
        elif c == " ":
            lines_per_page = 25
        else:
            lines_per_page = 1
