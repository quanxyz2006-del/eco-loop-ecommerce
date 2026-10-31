"""Small reusable repository for common SQLAlchemy operations."""

from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class Repository(Generic[ModelT]):
    """Encapsulate basic reads and persistence for one ORM model."""

    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def get(self, entity_id: int) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def first_by(self, **filters: Any) -> ModelT | None:
        statement = select(self.model).filter_by(**filters).limit(1)
        return self.session.scalar(statement)

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        return entity
