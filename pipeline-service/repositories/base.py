from typing import Generic, TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.customer_id == id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def count(self) -> int:
        return self.db.query(self.model).count()

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self,
        id: Any,
        obj_in: Dict[str, Any]
    ) -> Optional[ModelType]:
        db_obj = self.get(id)
        if not db_obj:
            return None

        for field, value in obj_in.items():
            setattr(db_obj, field, value)

        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: Any) -> bool:
        obj = self.get(id)
        if not obj:
            return False

        self.db.delete(obj)
        self.db.commit()
        return True

    def exists(self, id: Any) -> bool:
        return self.get(id) is not None

    def bulk_create(self, objects: List[Dict[str, Any]]) -> List[ModelType]:
        db_objs = [self.model(**obj) for obj in objects]
        self.db.add_all(db_objs)
        self.db.commit()
        return db_objs

    def get_or_create(
        self,
        id: Any,
        defaults: Dict[str, Any]
    ) -> tuple[ModelType, bool]:
        db_obj = self.get(id)
        if db_obj:
            return db_obj, False

        db_obj = self.model(**{**defaults, "customer_id": id})
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj, True
