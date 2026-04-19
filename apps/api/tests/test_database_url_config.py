from caseflow_api.settings import Settings


def test_database_url_config(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://tester:secret@db:5432/caseflow")

    settings = Settings()

    assert settings.database_url == "postgresql+psycopg://tester:secret@db:5432/caseflow"
