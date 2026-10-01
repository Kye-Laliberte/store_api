import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./pytest-import.db")
os.environ.setdefault("JWT_SECRET_KEY", "pytest-only-jwt-secret-key-for-tests-32-bytes")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models.ordermodels
import models.sqlAmodels as models
from api.main import app
from core.security import create_access_token
from database import get_db
from psycopg_models import UserStatus
from services.cart_services import pwd_context


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    models.Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        models.Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.fixture
def make_user(db_session):
    def factory(
        email="buyer@example.com",
        password="correct-horse-battery",
        status=UserStatus.active,
        is_admin=False,
    ):
        user = models.User(
            email=email,
            password_hash=pwd_context.hash(password),
            status=status,
            is_admin=is_admin,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return factory


@pytest.fixture
def make_item(db_session):
    def factory(name="widget", description="A useful widget", quantity=10, price=4.25):
        item = models.Item(
            name=name,
            description=description,
            quantity=quantity,
            price=price,
        )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)
        return item

    return factory


@pytest.fixture
def make_cart(db_session):
    def factory(user):
        cart = models.Cart(user_id=user.id)
        db_session.add(cart)
        db_session.commit()
        db_session.refresh(cart)
        return cart

    return factory


@pytest.fixture
def auth_headers():
    def factory(user):
        return {"Authorization": f"Bearer {create_access_token(user.id)}"}

    return factory