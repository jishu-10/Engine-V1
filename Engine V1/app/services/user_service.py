from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models import User


def get_or_create_user(db: Session, user_id: str | None = None) -> User:
    resolved_id = user_id or f"user_{uuid.uuid4().hex[:12]}"
    user = db.get(User, resolved_id)
    if user is None:
        user = User(id=resolved_id)
        db.add(user)
        db.flush()
    return user


def create_user(db: Session, user_id: str | None = None) -> User:
    user = get_or_create_user(db, user_id)
    db.commit()
    db.refresh(user)
    return user

