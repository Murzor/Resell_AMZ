import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
from app.main import app
from fastapi.testclient import TestClient

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client, db):
    """Crée un utilisateur et retourne les headers d'authentification"""
    from app.models.user import User
    from app.core.security import get_password_hash
    from app.core.config import settings
    
    user = User(
        username="test_user",
        hashed_password=get_password_hash("test_password"),
        is_active=True
    )
    db.add(user)
    db.commit()
    
    # Login
    response = client.post("/api/auth/login", json={"password": "test_password"})
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

