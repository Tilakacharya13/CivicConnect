from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import User


def test_admin_route_requires_admin_role(db_session, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-for-role-check-at-least-32-bytes")
    citizen = User(id=11, name="Citizen", email="c@example.test", password_hash="x", role="citizen")
    db_session.add(citizen)
    db_session.commit()
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as client:
        assert client.get("/admin/stats").status_code == 401
        from app.security import create_access_token
        token = create_access_token(citizen.id, "citizen")
        assert client.get("/admin/stats", headers={"Authorization": f"Bearer {token}"}).status_code == 403
    app.dependency_overrides.clear()
