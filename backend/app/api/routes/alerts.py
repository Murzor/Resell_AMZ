from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from app.workers.tasks import run_alert_task

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertResponse])
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alerts = db.query(Alert).all()
    return alerts


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte introuvable")
    return alert


@router.post("", response_model=AlertResponse)
def create_alert(
    alert_data: AlertCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = Alert(
        name=alert_data.name,
        description=alert_data.description,
        filters=alert_data.filters,
        is_active=True
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_data: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte introuvable")
    
    if alert_data.name is not None:
        alert.name = alert_data.name
    if alert_data.description is not None:
        alert.description = alert_data.description
    if alert_data.filters is not None:
        alert.filters = alert_data.filters
    if alert_data.is_active is not None:
        alert.is_active = alert_data.is_active
    
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}")
def delete_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte introuvable")
    
    db.delete(alert)
    db.commit()
    return {"message": "Alerte supprimée"}


@router.post("/{alert_id}/run")
def run_alert(
    alert_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alerte introuvable")
    
    if not alert.is_active:
        raise HTTPException(status_code=400, detail="Alerte inactive")
    
    # Mettre à jour last_run_at
    alert.last_run_at = datetime.utcnow()
    db.commit()
    
    # Lancer la tâche en arrière-plan via RQ
    from rq import Queue
    from redis import Redis
    from app.core.config import settings
    
    redis_conn = Redis.from_url(settings.REDIS_URL)
    queue = Queue("default", connection=redis_conn)
    job = queue.enqueue(run_alert_task, alert_id)
    
    return {"message": "Alerte lancée", "job_id": job.id}

