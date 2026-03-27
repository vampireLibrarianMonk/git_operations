"""Console/UI utilities."""

import itertools
import sys
import threading
import time


class Spinner:
    """Rotating spinner for long-running operations."""

    def __init__(self, message: str = ""):
        self.message = message
        self.spinning = False
        self.thread = None
        self.chars = itertools.cycle(["|", "/", "-", "\\"])

    def _spin(self):
        while self.spinning:
            sys.stdout.write(f"\r{self.message} {next(self.chars)}")
            sys.stdout.flush()
            time.sleep(0.1)
        # Clear the spinner line
        sys.stdout.write(f"\r{' ' * (len(self.message) + 2)}\r")
        sys.stdout.flush()

    def start(self, message: str = None):
        if message:
            self.message = message
        self.spinning = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()

    def stop(self):
        self.spinning = False
        if self.thread:
            self.thread.join()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()


def prompt_yes_no(question: str) -> bool:
    response = input(f"{question} [y/N]: ").strip().lower()
    return response in {"y", "yes"}
