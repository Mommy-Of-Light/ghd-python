#!/usr/bin/env python3
import os
from pathlib import Path
import stat, datetime

HISTFILE = Path.home() / ".pyhist"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


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
    import os
    n = len(lines)
    visible = lines_per_page
    last_was_blank = False

    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    while True:
        last_was_blank = False
        
        clear_screen()

        printed = 0
        for i in range(min(visible, n)):
            line = lines[i].rstrip("\r\n")

            # Collapse multiple blank lines
            if line == "":
                if last_was_blank:
                    continue
                print()
                last_was_blank = True
            else:
                print(line)
                last_was_blank = False

            printed += 1

        if visible >= n:
            return

        c = input("--More-- (Enter=+1 line, Space=+25 lines, 'end'=show all, q=quit) ")
        if c == "q":
            return
        elif c == " ":
            visible += lines_per_page
        elif c.lower() == "end":
            visible = n
        else:
            visible += 1
