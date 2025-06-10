"""
Terminal Utilities for Keyboard Interaction.

This module provides a cross-platform context manager for disabling
terminal echo during keyboard-controlled audio synthesis sessions.

Author: Valerio Poggi - 2025
"""

import sys


class TerminalSilent:
    """
    Context manager to disable terminal input echo on Unix systems.

    On Unix, this sets the terminal to raw mode to avoid echoing
    typed characters. On Windows, it performs no action.
    """

    def __enter__(self):
        self.platform = sys.platform
        if self.platform.startswith("linux") or self.platform == "darwin":
            import termios
            import tty
            self.fd = sys.stdin.fileno()
            self.old_settings = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)
            self.termios = termios
        elif self.platform == "win32":
            import msvcrt
            self.msvcrt = msvcrt
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.platform.startswith("linux") or self.platform == "darwin":
            self.termios.tcsetattr(
                self.fd,
                self.termios.TCSADRAIN,
                self.old_settings
            )

