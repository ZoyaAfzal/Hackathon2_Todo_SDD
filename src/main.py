"""
Main entry point for the Todo Application - Phase I.

Provides an interactive command-line interface for todo management.
"""

import sys
from typing import Optional

from src.state.store import TaskStore
from src.cli.parser import TodoParser
from src.cli.formatter import format_error


def print_welcome() -> None:
    """Display welcome message."""
    print("=" * 60)
    print("TODO APPLICATION - PHASE I")
    print("In-Memory Console Todo Manager")
    print("=" * 60)
    print("Type 'help' for available commands, 'exit' to quit")
    print()


def main() -> int:
    """
    Main application entry point with interactive REPL mode.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Initialize state
    store = TaskStore()
    parser = TodoParser(store)

    # Print welcome banner
    print_welcome()

    # Interactive mode
    while True:
        try:
            # Read user input
            user_input = input("todo> ").strip()

            # Skip empty lines
            if not user_input:
                continue

            # Parse and execute command
            # Split input into arguments (simple split by spaces)
            args = user_input.split()
            result, should_exit = parser.parse_and_execute(args)

            # Display result
            if result:
                print(result)

            # Exit if requested
            if should_exit:
                return 0

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'exit' to quit gracefully.")
            continue

        except EOFError:
            print("\n\nGoodbye!")
            return 0

        except SystemExit as e:
            # Catch SystemExit from exit command
            if e.code == 0:
                return 0
            # For other SystemExit (like from argparse), continue
            continue

        except Exception as e:
            # Catch unexpected errors
            print(format_error(f"Unexpected error: {str(e)}"))
            continue


if __name__ == "__main__":
    sys.exit(main())
