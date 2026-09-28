"""Test suite for Duewright.

Mirrors the source modules (models, service, storage, cli, api). Service tests
are parametrized over both repository implementations; API tests use
FastAPI's `TestClient` with `app.dependency_overrides`; CLI tests feed
`builtins.input` via `monkeypatch` and assert output via `capsys`.
"""
