from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import Complaint, Notification, User
from app.security import create_access_token, hash_password
import app.services.uploads as upload_service

JPEG = b"\xff\xd8\xff\xe0" + b"test-image-data"


def setup_client(db_session, monkeypatch, tmp_path):
    monkeypatch.setenv("JWT_SECRET_KEY", "pytest-feature-secret-key-long-enough-for-hs256")
    monkeypatch.setattr(upload_service, "UPLOADS_DIR", tmp_path)
    citizen = User(name="Feature Citizen", email="feature@example.com", password_hash=hash_password("FeaturePass!1"), role="citizen")
    other = User(name="Other Citizen", email="other@example.com", password_hash=hash_password("FeaturePass!1"), role="citizen")
    admin = User(name="Feature Admin", email="admin-feature@example.com", password_hash=hash_password("FeaturePass!1"), role="admin")
    db_session.add_all([citizen, other, admin])
    db_session.flush()

    def new_complaint(owner, title, status="Reported"):
        now = datetime.now(timezone.utc)
        item = Complaint(
            user_id=owner.id, title=title, description="test issue", category="Road", location="QA Street",
            severity="Medium", priority_score=40, priority_label="Medium", status=status,
            duplicate_count=0, sla_target_hours=168, expected_resolution_at=now + timedelta(days=7),
            is_overdue=False, resolved_at=now if status == "Resolved" else None,
        )
        db_session.add(item)
        db_session.flush()
        return item

    first = new_complaint(citizen, "Blocked drain")
    another = new_complaint(citizen, "Resolved issue", "Resolved")
    other_complaint = new_complaint(other, "Other person's complaint")
    db_session.commit()
    app.dependency_overrides[get_db] = lambda: db_session
    tokens = {
        "citizen": create_access_token(citizen.id, "citizen"),
        "other": create_access_token(other.id, "citizen"),
        "admin": create_access_token(admin.id, "admin"),
    }
    client = TestClient(app)
    return client, tokens, citizen, other, admin, first, another, other_complaint


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_photo_feedback_notifications_ownership_and_roles(db_session, monkeypatch, tmp_path):
    client, tokens, citizen, other, admin, complaint, resolved, foreign = setup_client(db_session, monkeypatch, tmp_path)
    try:
        # Valid image and public static URL.
        response = client.post(f"/complaints/{complaint.id}/photo", headers=auth(tokens["citizen"]), files={"file": ("anything.jpg", JPEG, "image/jpeg")})
        assert response.status_code == 200
        before_url = response.json()["photo_url_before"]
        assert before_url.startswith("/uploads/") and (tmp_path / before_url.rsplit("/", 1)[1]).read_bytes() == JPEG
        assert client.post(f"/complaints/{complaint.id}/photo", headers=auth(tokens["citizen"]), files={"file": ("bad.txt", b"not an image", "text/plain")}).status_code == 415
        huge = b"\xff\xd8\xff" + b"x" * (5 * 1024 * 1024)
        assert client.post(f"/complaints/{complaint.id}/photo", headers=auth(tokens["citizen"]), files={"file": ("huge.jpg", huge, "image/jpeg")}).status_code == 413
        assert client.post(f"/complaints/{complaint.id}/photo", headers=auth(tokens["other"]), files={"file": ("image.jpg", JPEG, "image/jpeg")}).status_code == 404

        # Feedback must be resolved and can only be submitted once by its owner.
        assert client.post(f"/complaints/{complaint.id}/feedback", headers=auth(tokens["citizen"]), json={"rating": 5}).status_code == 409
        feedback = client.post(f"/complaints/{resolved.id}/feedback", headers=auth(tokens["citizen"]), json={"rating": 4, "comment": "Fixed well"})
        assert feedback.status_code == 200 and feedback.json()["feedback_rating"] == 4
        assert client.post(f"/complaints/{resolved.id}/feedback", headers=auth(tokens["citizen"]), json={"rating": 3}).status_code == 409
        assert client.post(f"/complaints/{resolved.id}/feedback", headers=auth(tokens["other"]), json={"rating": 1}).status_code == 404

        # Admin status changes write an owner-scoped notification.
        status_change = client.patch(f"/admin/complaints/{complaint.id}/status", headers=auth(tokens["admin"]), json={"status": "In Progress", "comment": "Crew assigned"})
        assert status_change.status_code == 200
        notifications = client.get("/notifications", headers=auth(tokens["citizen"])).json()
        assert notifications["unread_count"] == 1
        notice = notifications["notifications"][0]
        assert notice["message"] == "Your complaint 'Blocked drain' is now In Progress"
        assert client.get("/notifications", headers=auth(tokens["other"])).json() == {"unread_count": 0, "notifications": []}
        assert client.patch(f"/notifications/{notice['id']}/read", headers=auth(tokens["other"])).status_code == 404
        assert client.patch(f"/notifications/{notice['id']}/read", headers=auth(tokens["citizen"])).json()["unread_count"] == 0

        client.patch(f"/admin/complaints/{complaint.id}/status", headers=auth(tokens["admin"]), json={"status": "Verified"})
        read_all = client.patch("/notifications/read-all", headers=auth(tokens["citizen"])).json()
        assert read_all["unread_count"] == 0 and all(item["is_read"] for item in read_all["notifications"])

        # Admin after-photo uses the same image validation; citizens cannot use the route.
        resolve = client.patch(f"/admin/complaints/{resolved.id}/status", headers=auth(tokens["admin"]), json={"status": "Resolved"})
        assert resolve.status_code == 200
        after = client.post(f"/admin/complaints/{resolved.id}/after-photo", headers=auth(tokens["admin"]), files={"file": ("after.jpg", JPEG, "image/jpeg")})
        assert after.status_code == 200 and after.json()["photo_url_after"].startswith("/uploads/")
        assert client.post(f"/admin/complaints/{resolved.id}/after-photo", headers=auth(tokens["admin"]), files={"file": ("bad.txt", b"no", "text/plain")}).status_code == 415
        assert client.post(f"/admin/complaints/{resolved.id}/after-photo", headers=auth(tokens["citizen"]), files={"file": ("after.jpg", JPEG, "image/jpeg")}).status_code == 403

        # Login response exposes role and /auth/me continues to expose it too.
        login = client.post("/auth/login", json={"email": "admin-feature@example.com", "password": "FeaturePass!1"})
        assert login.status_code == 200 and login.json()["role"] == "admin"
        assert client.get("/auth/me", headers=auth(login.json()["access_token"])).json()["role"] == "admin"
    finally:
        # The temporary folder is removed by pytest's tmp_path fixture.
        client.close()
        app.dependency_overrides.clear()
