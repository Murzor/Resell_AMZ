from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.settings import Settings as SettingsModel
from app.schemas.settings import SettingsCreate, SettingsUpdate, SettingsResponse

router = APIRouter(prefix="/api/settings", tags=["settings"])


@router.get("", response_model=List[SettingsResponse])
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    settings = db.query(SettingsModel).all()
    return settings


@router.get("/{key}", response_model=SettingsResponse)
def get_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    setting = db.query(SettingsModel).filter(SettingsModel.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Paramètre introuvable")
    return setting


@router.post("", response_model=SettingsResponse)
def create_setting(
    setting_data: SettingsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(SettingsModel).filter(SettingsModel.key == setting_data.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Paramètre déjà existant")
    
    setting = SettingsModel(key=setting_data.key, value=setting_data.value)
    db.add(setting)
    db.commit()
    db.refresh(setting)
    return setting


@router.put("/{key}", response_model=SettingsResponse)
def update_setting(
    key: str,
    setting_data: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    setting = db.query(SettingsModel).filter(SettingsModel.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Paramètre introuvable")
    
    setting.value = setting_data.value
    db.commit()
    db.refresh(setting)
    return setting


@router.delete("/{key}")
def delete_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    setting = db.query(SettingsModel).filter(SettingsModel.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Paramètre introuvable")
    
    db.delete(setting)
    db.commit()
    return {"message": "Paramètre supprimé"}

