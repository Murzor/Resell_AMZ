from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.list import List as ListModel, ListItem
from app.models.product import Product
from app.schemas.list import ListCreate, ListUpdate, ListResponse, ListItemCreate, ListItemResponse
import csv
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/api/lists", tags=["lists"])


@router.get("", response_model=List[ListResponse])
def get_lists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    lists = db.query(ListModel).all()
    result = []
    for list_item in lists:
        items = db.query(ListItem).filter(ListItem.list_id == list_item.id).all()
        items_data = []
        for item in items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            items_data.append(ListItemResponse(
                id=item.id,
                product_id=item.product_id,
                asin=product.asin if product else "",
                title=product.title if product else None,
                notes=item.notes,
                created_at=item.created_at
            ))
        result.append(ListResponse(
            id=list_item.id,
            name=list_item.name,
            description=list_item.description,
            items=items_data,
            created_at=list_item.created_at,
            updated_at=list_item.updated_at
        ))
    return result


@router.get("/{list_id}", response_model=ListResponse)
def get_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    list_item = db.query(ListModel).filter(ListModel.id == list_id).first()
    if not list_item:
        raise HTTPException(status_code=404, detail="Liste introuvable")
    
    items = db.query(ListItem).filter(ListItem.list_id == list_id).all()
    items_data = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items_data.append(ListItemResponse(
            id=item.id,
            product_id=item.product_id,
            asin=product.asin if product else "",
            title=product.title if product else None,
            notes=item.notes,
            created_at=item.created_at
        ))
    
    return ListResponse(
        id=list_item.id,
        name=list_item.name,
        description=list_item.description,
        items=items_data,
        created_at=list_item.created_at,
        updated_at=list_item.updated_at
    )


@router.post("", response_model=ListResponse)
def create_list(
    list_data: ListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    list_item = ListModel(
        name=list_data.name,
        description=list_data.description
    )
    db.add(list_item)
    db.commit()
    db.refresh(list_item)
    return ListResponse(
        id=list_item.id,
        name=list_item.name,
        description=list_item.description,
        items=[],
        created_at=list_item.created_at,
        updated_at=list_item.updated_at
    )


@router.put("/{list_id}", response_model=ListResponse)
def update_list(
    list_id: int,
    list_data: ListUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    list_item = db.query(ListModel).filter(ListModel.id == list_id).first()
    if not list_item:
        raise HTTPException(status_code=404, detail="Liste introuvable")
    
    if list_data.name is not None:
        list_item.name = list_data.name
    if list_data.description is not None:
        list_item.description = list_data.description
    
    db.commit()
    db.refresh(list_item)
    
    items = db.query(ListItem).filter(ListItem.list_id == list_id).all()
    items_data = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        items_data.append(ListItemResponse(
            id=item.id,
            product_id=item.product_id,
            asin=product.asin if product else "",
            title=product.title if product else None,
            notes=item.notes,
            created_at=item.created_at
        ))
    
    return ListResponse(
        id=list_item.id,
        name=list_item.name,
        description=list_item.description,
        items=items_data,
        created_at=list_item.created_at,
        updated_at=list_item.updated_at
    )


@router.delete("/{list_id}")
def delete_list(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    list_item = db.query(ListModel).filter(ListModel.id == list_id).first()
    if not list_item:
        raise HTTPException(status_code=404, detail="Liste introuvable")
    
    db.delete(list_item)
    db.commit()
    return {"message": "Liste supprimée"}


@router.post("/{list_id}/items", response_model=ListItemResponse)
def add_item(
    list_id: int,
    item_data: ListItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    list_item = db.query(ListModel).filter(ListModel.id == list_id).first()
    if not list_item:
        raise HTTPException(status_code=404, detail="Liste introuvable")
    
    product = db.query(Product).filter(Product.id == item_data.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    
    item = ListItem(
        list_id=list_id,
        product_id=item_data.product_id,
        notes=item_data.notes
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return ListItemResponse(
        id=item.id,
        product_id=item.product_id,
        asin=product.asin,
        title=product.title,
        notes=item.notes,
        created_at=item.created_at
    )


@router.delete("/{list_id}/items/{item_id}")
def delete_item(
    list_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(ListItem).filter(
        ListItem.id == item_id,
        ListItem.list_id == list_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Élément introuvable")
    
    db.delete(item)
    db.commit()
    return {"message": "Élément supprimé"}


@router.get("/{list_id}/export/csv")
def export_list_csv(
    list_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    list_item = db.query(ListModel).filter(ListModel.id == list_id).first()
    if not list_item:
        raise HTTPException(status_code=404, detail="Liste introuvable")
    
    items = db.query(ListItem).filter(ListItem.list_id == list_id).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ASIN", "Titre", "Notes"])
    
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        writer.writerow([
            product.asin if product else "",
            product.title if product else "",
            item.notes or ""
        ])
    
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=list_{list_id}.csv"}
    )


@router.post("/{list_id}/export/google-sheets")
def export_list_google_sheets(
    list_id: int,
    webhook_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Cette fonction devrait envoyer les données à un webhook
    # L'implémentation réelle dépendrait de l'API Google Sheets utilisée
    import httpx
    
    list_item = db.query(ListModel).filter(ListModel.id == list_id).first()
    if not list_item:
        raise HTTPException(status_code=404, detail="Liste introuvable")
    
    items = db.query(ListItem).filter(ListItem.list_id == list_id).all()
    data = []
    for item in items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        data.append({
            "asin": product.asin if product else "",
            "title": product.title if product else "",
            "notes": item.notes or ""
        })
    
    # Envoyer les données au webhook
    try:
        with httpx.Client() as client:
            response = client.post(webhook_url, json={"items": data}, timeout=10.0)
            response.raise_for_status()
        return {"message": "Export vers Google Sheets réussi", "items_count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'export: {str(e)}")

