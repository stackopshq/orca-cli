"""``shark baby`` — easter egg: animated baby shark."""

from __future__ import annotations

import time
import click
from rich.console import Console

console = Console()


@click.command("baby", hidden=True)
@click.pass_context
def baby(ctx: click.Context) -> None:
    """🦈 Baby shark! 🎶"""
    frames = [
        """
    .--.
   |o_o |
   |:_/ |
  //   \\ \\
 (|     | )
/'\\_   _/`\\
\\___)=(___/
        🎵 Baby shark, doo doo doo doo doo...
""",
        """
    .--.
   |o_o |
   |:_/ |
  //   \\ \\
 (|     | )
/'\\_   _/`\\
\\___)=(___/
        🎵 Baby shark, doo doo doo doo doo...
        🎵 Baby shark, doo doo doo doo doo...
""",
        """
    .--.
   |o_o |
   |:_/ |
  //   \\ \\
 (|     | )
/'\\_   _/`\\
\\___)=(___/
        🎵 Baby shark, doo doo doo doo doo...
        🎵 Baby shark, doo doo doo doo doo...
        🎵 Baby shark! 🦈
""",
        """
    .--.
   |O_O |
   |:_/ |
  //   \\ \\
 (|     | )
/'\\_   _/`\\
\\___)=(___/
        🎵 Mommy shark, doo doo doo doo doo...
""",
        """
    .--.
   |O_O |
   |:_/ |
  //   \\ \\
 (|     | )
/'\\_   _/`\\
\\___)=(___/
        🎵 Mommy shark, doo doo doo doo doo...
        🎵 Mommy shark! 🦈
""",
        """
    .--.
   |^_^ |
   |:_/ |
  //   \\ \\
 (|     | )
/'\\_   _/`\\
\\___)=(___/
        🎵 Daddy shark, doo doo doo doo doo...
        🎵 Daddy shark! 🦈
""",
        """
    .--.
   |o_o |
   |:_/ |
  //   \\ \\
 (|     | )
/'\\_   _/`\\
\\___)=(___/
        🎵 Going on a hunt, doo doo doo doo doo...
        🎵 Run away, run away! 🏃‍♂️
""",
        """
    .--.
   |O_O |
   |:_/ |
  //   \\ \\
 (|     | )
/'\\_   _/`\\
\\___)=(___/
        🎵 Safe at last, doo doo doo doo doo...
        🎵 It's the end! 🎉
""",
    ]

    for frame in frames:
        console.clear()
        console.print(frame, style="cyan")
        time.sleep(1.5)

    console.clear()
    console.print("🦈 Baby shark! 🦈", style="bold cyan")
    console.print("🎶 Doo doo doo doo doo... 🎶", style="magenta")
