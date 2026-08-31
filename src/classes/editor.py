import curses
from pathlib import Path


class TerminalEditor:
    def __init__(self, path: Path):
        self.path = path
        self.lines = []
        self.cursor_y = 0
        self.cursor_x = 0
        self.scroll_y = 0
        self.modified = False

        if self.path.exists():
            self.lines = self.path.read_text(
                encoding="utf-8",
                errors="replace"
            ).splitlines()

        if not self.lines:
            self.lines = [""]

    def save(self):
        self.path.write_text(
            "\n".join(self.lines) + "\n",
            encoding="utf-8"
        )
        self.modified = False

    def run(self):
        curses.wrapper(self._editor)

    def _editor(self, stdscr):
        curses.raw()
        curses.noecho()
        stdscr.keypad(True)

        while True:
            self.draw(stdscr)

            key = stdscr.getch()

            # Ctrl+Q
            if key == 17:
                if self.modified:
                    self.save()
                break

            # Ctrl+S
            elif key == 19:
                self.save()

            # Arrow keys
            elif key == curses.KEY_UP:
                self.cursor_y = max(0, self.cursor_y - 1)
                self.fix_cursor()

            elif key == curses.KEY_DOWN:
                self.cursor_y = min(
                    len(self.lines) - 1,
                    self.cursor_y + 1
                )
                self.fix_cursor()

            elif key == curses.KEY_LEFT:
                if self.cursor_x > 0:
                    self.cursor_x -= 1
                elif self.cursor_y > 0:
                    self.cursor_y -= 1
                    self.cursor_x = len(self.lines[self.cursor_y])

            elif key == curses.KEY_RIGHT:
                if self.cursor_x < len(self.lines[self.cursor_y]):
                    self.cursor_x += 1
                elif self.cursor_y < len(self.lines) - 1:
                    self.cursor_y += 1
                    self.cursor_x = 0

            # Enter
            elif key in (10, 13):
                current = self.lines[self.cursor_y]

                left = current[:self.cursor_x]
                right = current[self.cursor_x:]

                self.lines[self.cursor_y] = left
                self.lines.insert(self.cursor_y + 1, right)

                self.cursor_y += 1
                self.cursor_x = 0
                self.modified = True

            # Backspace
            elif key in (8, 127, curses.KEY_BACKSPACE):
                if self.cursor_x > 0:
                    line = self.lines[self.cursor_y]

                    self.lines[self.cursor_y] = (
                        line[:self.cursor_x - 1]
                        + line[self.cursor_x:]
                    )

                    self.cursor_x -= 1
                    self.modified = True

                elif self.cursor_y > 0:
                    previous_length = len(
                        self.lines[self.cursor_y - 1]
                    )

                    self.lines[self.cursor_y - 1] += (
                        self.lines[self.cursor_y]
                    )

                    del self.lines[self.cursor_y]

                    self.cursor_y -= 1
                    self.cursor_x = previous_length
                    self.modified = True

            # Delete
            elif key == curses.KEY_DC:
                line = self.lines[self.cursor_y]

                if self.cursor_x < len(line):
                    self.lines[self.cursor_y] = (
                        line[:self.cursor_x]
                        + line[self.cursor_x + 1:]
                    )
                    self.modified = True

                elif self.cursor_y < len(self.lines) - 1:
                    self.lines[self.cursor_y] += (
                        self.lines[self.cursor_y + 1]
                    )

                    del self.lines[self.cursor_y + 1]
                    self.modified = True

            # Normal characters
            elif 32 <= key <= 126:
                line = self.lines[self.cursor_y]

                self.lines[self.cursor_y] = (
                    line[:self.cursor_x]
                    + chr(key)
                    + line[self.cursor_x:]
                )

                self.cursor_x += 1
                self.modified = True

    def fix_cursor(self):
        self.cursor_x = min(
            self.cursor_x,
            len(self.lines[self.cursor_y])
        )

    def draw(self, stdscr):
        stdscr.erase()

        height, width = stdscr.getmaxyx()

        # Header
        title = f" {self.path.name}"
        if self.modified:
            title += " [+]"

        stdscr.addnstr(0, 0, title, width - 1)

        # Editor
        visible_height = height - 2

        if self.cursor_y < self.scroll_y:
            self.scroll_y = self.cursor_y

        if self.cursor_y >= self.scroll_y + visible_height:
            self.scroll_y = (
                self.cursor_y - visible_height + 1
            )

        for screen_y in range(visible_height):
            line_y = self.scroll_y + screen_y

            if line_y >= len(self.lines):
                break

            line_number = f"{line_y + 1:4} "

            stdscr.addnstr(
                screen_y + 1,
                0,
                line_number,
                width - 1
            )

            stdscr.addnstr(
                screen_y + 1,
                5,
                self.lines[line_y],
                width - 6
            )

        # Footer
        footer = " Ctrl+S Save | Ctrl+Q Quit "

        stdscr.addnstr(
            height - 1,
            0,
            footer,
            width - 1
        )

        cursor_screen_y = (
            self.cursor_y - self.scroll_y + 1
        )

        cursor_screen_x = 5 + self.cursor_x

        try:
            stdscr.move(
                cursor_screen_y,
                min(cursor_screen_x, width - 1)
            )
        except curses.error:
            pass

        stdscr.refresh()