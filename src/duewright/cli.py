"""Interactive command-line interface.

Implemented in Phase 3 (tasks/plan.md, Task 3.1): the menu loop from the brief's
flowchart — load, show menu, add/update/delete with re-prompting input helpers,
save, display the updated list, continue — with top-level handling for
`TaskNotFoundError`, `StorageError`, and `KeyboardInterrupt`/`EOFError`.

The CLI is an adapter: it owns prompts and printing and holds no business rules.
"""


def main() -> int:
    """Entry point for the `duewright` console script (Phase 3 placeholder)."""
    print("Duewright CLI arrives in Phase 3. See tasks/plan.md.")
    return 0
