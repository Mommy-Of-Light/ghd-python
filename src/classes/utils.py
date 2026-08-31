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
    import sys
    import readline

    n = len(lines)
    visible = lines_per_page

    def clear_screen():
        os.system("cls" if os.name == "nt" else "clear")

    def clear_pager_line():
        """
        Clear the current terminal line and move the cursor to column 0.
        """
        if os.name == "nt":
            # Windows console
            print("\r" + " " * 120 + "\r", end="", flush=True)
        else:
            # Linux / Unix terminal
            print("\033[2K\r", end="", flush=True)

    def pager_input():
        """
        Read pager input without using readline history.
        """

        if os.name == "nt":
            import msvcrt

            chars = []

            while True:
                char = msvcrt.getwch()

                # Enter
                if char in ("\r", "\n"):
                    print()
                    return ""

                # Space
                if char == " ":
                    print()
                    return " "

                # q
                if char.lower() == "q":
                    print("q")
                    return "q"

                # Backspace
                if char == "\b":
                    if chars:
                        chars.pop()
                        print("\b \b", end="", flush=True)
                    continue

                # Normal character
                if char.isprintable():
                    chars.append(char)
                    print(char, end="", flush=True)

                    # "end"
                    if "".join(chars).lower() == "end":
                        print()
                        return "end"

        else:
            import termios
            import tty

            chars = []

            old_settings = termios.tcgetattr(sys.stdin)

            try:
                tty.setraw(sys.stdin.fileno())

                while True:
                    char = sys.stdin.read(1)

                    # Enter
                    if char in ("\r", "\n"):
                        print()
                        return ""

                    # Space
                    if char == " ":
                        print()
                        return " "

                    # q
                    if char.lower() == "q":
                        print("q")
                        return "q"

                    # Backspace
                    if char in ("\x7f", "\b"):
                        if chars:
                            chars.pop()
                            print("\b \b", end="", flush=True)
                        continue

                    # Normal character
                    if char.isprintable():
                        chars.append(char)
                        print(char, end="", flush=True)

                        # "end"
                        if "".join(chars).lower() == "end":
                            print()
                            return "end"

            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    while True:
        clear_screen()

        last_was_blank = False

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

        # Everything has been displayed
        if visible >= n:
            return

        # Pager prompt
        print(
            "--More-- " "(Enter=+1 line, Space=+25 lines, " "'end'=show all, q=quit) ",
            end="",
            flush=True,
        )

        c = pager_input()

        # Clear the pager line before returning/continuing
        clear_pager_line()

        if c == "q":
            return

        elif c == " ":
            visible += lines_per_page

        elif c.lower() == "end":
            visible = n

        else:
            # Enter
            visible += 1
