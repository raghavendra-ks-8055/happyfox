import json
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models.rule import Rule, Condition, Action


# Create an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    # Create the database tables
    Base.metadata.create_all(bind=engine)

    # Create a test client
    with TestClient(app) as c:
        yield c

    # Drop the database tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def db():
    # Create a database session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def rule(db):
    # Create a test rule
    rule = Rule(name="Test Rule", match_type="all")
    db.add(rule)
    db.flush()

    # Create conditions
    condition1 = Condition(
        rule_id=rule.id,
        field="from",
        predicate="contains",
        value="tenmiles.com",
        unit=None,
    )
    db.add(condition1)

    condition2 = Condition(
        rule_id=rule.id,
        field="subject",
        predicate="contains",
        value="Interview",
        unit=None,
    )
    db.add(condition2)

    # Create actions
    action1 = Action(rule_id=rule.id, type="move_message", target="Inbox")
    db.add(action1)

    action2 = Action(rule_id=rule.id, type="mark_as_read", target=None)
    db.add(action2)

    db.commit()
    db.refresh(rule)

    return rule


def test_get_rules(client, rule):
    response = client.get("/api/rules")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Test Rule"
    assert data[0]["match_type"] == "all"
    assert len(data[0]["conditions"]) == 2
    assert len(data[0]["actions"]) == 2


def test_get_rule(client, rule):
    response = client.get(f"/api/rules/{rule.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Test Rule"
    assert data["match_type"] == "all"
    assert len(data["conditions"]) == 2
    assert len(data["actions"]) == 2


def test_get_rule_not_found(client):
    response = client.get("/api/rules/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_create_rule(client):
    rule_data = {
        "name": "New Rule",
        "match_type": "any",
        "conditions": [
            {"field": "from", "predicate": "contains", "value": "example.com"}
        ],
        "actions": [{"type": "mark_as_unread"}],
    }

    response = client.post("/api/rules", json=rule_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "New Rule"
    assert data["match_type"] == "any"
    assert len(data["conditions"]) == 1
    assert len(data["actions"]) == 1


def test_update_rule(client, rule):
    rule_data = {"name": "Updated Rule", "match_type": "any"}

    response = client.put(f"/api/rules/{rule.id}", json=rule_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Rule"
    assert data["match_type"] == "any"
    assert len(data["conditions"]) == 2
    assert len(data["actions"]) == 2


def test_update_rule_not_found(client):
    rule_data = {"name": "Updated Rule", "match_type": "any"}

    response = client.put(
        "/api/rules/00000000-0000-0000-0000-000000000000", json=rule_data
    )
    assert response.status_code == 404


def test_delete_rule(client, rule):
    response = client.delete(f"/api/rules/{rule.id}")
    assert response.status_code == 204

    # Verify the rule was deleted
    response = client.get(f"/api/rules/{rule.id}")
    assert response.status_code == 404


def test_delete_rule_not_found(client):
    response = client.delete("/api/rules/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_process_email(client, rule, db):
    # Create a new rule for this test
    new_rule = Rule(name="Process Email Test Rule", match_type="all")
    db.add(new_rule)
    db.flush()

    # Create conditions
    condition = Condition(
        rule_id=new_rule.id,
        field="from",
        predicate="contains",
        value="tenmiles.com",
        unit=None,
    )
    db.add(condition)

    # Create actions
    action = Action(rule_id=new_rule.id, type="mark_as_read", target=None)
    db.add(action)

    db.commit()
    db.refresh(new_rule)

    # Test with a matching email
    email_data = {
        "from": "test@tenmiles.com",
        "subject": "Test Email",
        "message": "This is a test email.",
        "received_date": datetime.utcnow().isoformat(),
    }

    response = client.post("/api/process-email", json=email_data)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "mark_as_read"

    # Test with a non-matching email
    email_data["from"] = "test@example.com"

    response = client.post("/api/process-email", json=email_data)
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 0
