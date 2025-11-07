import pytest
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token, decode_access_token
from datetime import timedelta


def test_password_hashing():
    """Test du hachage de mot de passe"""
    password = "test_password"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_jwt_token():
    """Test de création et décodage de token JWT"""
    data = {"sub": "test_user"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "test_user"
    assert "exp" in decoded


def test_jwt_token_expired():
    """Test avec un token expiré (simulation)"""
    from app.core.config import settings
    from jose import jwt
    from datetime import datetime, timedelta
    
    # Créer un token expiré
    expire = datetime.utcnow() - timedelta(minutes=1)
    to_encode = {"sub": "test_user", "exp": expire}
    token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    decoded = decode_access_token(token)
    assert decoded is None  # Token expiré devrait retourner None

