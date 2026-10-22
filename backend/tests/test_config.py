import pytest
from pydantic import ValidationError

from app.core.config import Settings


def make(url: str) -> Settings:
    return Settings(_env_file=None, database_url=url)


def test_accepts_restricted_role():
    assert make("postgresql://query_readonly:pw@localhost:5432/db").sql_max_rows == 100


def test_accepts_supabase_pooler_username():
    make("postgresql://query_readonly.abcdefgh:pw@aws-0.pooler.supabase.com:6543/postgres")


@pytest.mark.parametrize("user", ["postgres", "service_role", "supabase_admin", "postgres.abcdefgh"])
def test_rejects_privileged_roles(user):
    with pytest.raises(ValidationError):
        make(f"postgresql://{user}:pw@localhost:5432/db")


def test_rejects_wrong_scheme():
    with pytest.raises(ValidationError):
        make("mysql://query_readonly:pw@localhost/db")


def test_rejects_unreasonable_timeout():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url="postgresql://query_readonly:pw@h/db",
                 sql_statement_timeout_ms=10)