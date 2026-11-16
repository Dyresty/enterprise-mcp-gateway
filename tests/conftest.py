import pytest

from app.mcp import server


@pytest.fixture(autouse=True)
def capture_audit_log(monkeypatch):
    """
    Keep pipeline tests out of the real audit table.
    Audit records are collected in memory so tests can assert on them.
    test_execution_logger.py uses its own logger and still writes to PostgreSQL.
    """

    records = []

    monkeypatch.setattr(
        server.execution_logger,
        "log_execution",
        lambda **record: records.append(record),
    )

    return records
