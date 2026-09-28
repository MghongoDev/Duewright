"""Phase 0 smoke test: prove the toolchain before any feature exists.

The guide's checkpoint for Phase 0 is trivial by design — a green test run
against an empty-but-professional repo. This placeholder asserts the package
imports, its metadata is wired, and the console script target resolves. It is
replaced by real tests from Phase 1 on (tasks/plan.md).
"""

import duewright


def test_package_imports_and_reports_version() -> None:
    assert duewright.__version__ == "0.1.0"


def test_console_script_target_is_importable() -> None:
    from duewright import cli

    assert callable(cli.main)
