from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import Login, Token
from app.core.security import get_password_hash

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(login_data: Login, db: Session = Depends(get_db)):
    # Vérifier si l'utilisateur admin existe, sinon le créer
    user = db.query(User).filter(User.username == "admin").first()
    if not user:
        user = User(
            username="admin",
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Vérifier le mot de passe
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe incorrect"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utilisateur inactif"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

