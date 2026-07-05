from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.dependencies import get_db
from webhooks.models import WebhookSubscription

router = APIRouter()


class SubscriptionCreate(BaseModel):
    name: str
    url: str
    secret: str | None = None
    events: str | None = None


class SubscriptionResponse(BaseModel):
    id: str
    name: str
    url: str
    events: str | None
    active: bool

    model_config = {"from_attributes": True}


@router.post("/webhooks", response_model=SubscriptionResponse)
def create_subscription(data: SubscriptionCreate, db: Session = Depends(get_db)):
    sub = WebhookSubscription(
        name=data.name,
        url=data.url,
        secret=data.secret,
        events=data.events,
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub


@router.get("/webhooks", response_model=list[SubscriptionResponse])
def list_subscriptions(db: Session = Depends(get_db)):
    return db.query(WebhookSubscription).all()


@router.delete("/webhooks/{sub_id}", status_code=204)
def delete_subscription(sub_id: str, db: Session = Depends(get_db)):
    sub = db.query(WebhookSubscription).filter(WebhookSubscription.id == sub_id).first()
    if not sub:
        raise HTTPException(404, "Webhook não encontrado")
    db.delete(sub)
    db.commit()
