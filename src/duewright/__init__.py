"""Duewright: a task manager with one tested core and two interfaces.

Layers (see ADR-002, docs/decisions/):

    models / validation / service / storage   -- stdlib-only core, no I/O
    cli                                       -- interactive menu (Phase 3)
    api                                       -- FastAPI REST API (Phase 4)

The brief is the implementation guide; requirements live in SPEC.md, the
build order in tasks/plan.md.
"""

__version__ = "0.1.0"
