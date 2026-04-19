from caseflow_api.models import AuditLog, Document, DocumentChunk, Matter, Organisation, User


def test_model_imports() -> None:
    assert Organisation.__tablename__ == "organisations"
    assert User.__tablename__ == "users"
    assert Matter.__tablename__ == "matters"
    assert Document.__tablename__ == "documents"
    assert DocumentChunk.__tablename__ == "document_chunks"
    assert AuditLog.__tablename__ == "audit_logs"
