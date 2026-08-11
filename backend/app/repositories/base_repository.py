"""
Generic Base Repository

Provides reusable CRUD operations.
"""

from typing import Generic, Optional, Type, TypeVar

from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Generic repository for CRUD operations.
    """

    def __init__(
        self,
        model: Type[ModelType],
        db: Session,
    ):
        self.model = model
        self.db = db

    # -----------------------------------------------------

    def get(self, obj_id: int) -> Optional[ModelType]:

        return (
            self.db.query(self.model)
            .filter(self.model.id == obj_id)
            .first()
        )

    # -----------------------------------------------------

    def get_all(self):

        return self.db.query(self.model).all()

    # -----------------------------------------------------

    def create(
        self,
        obj: ModelType,
    ) -> ModelType:

        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)

        return obj

    # -----------------------------------------------------

    def update(
        self,
        obj: ModelType,
    ) -> ModelType:

        self.db.commit()
        self.db.refresh(obj)

        return obj

    # -----------------------------------------------------

    def delete(
        self,
        obj: ModelType,
    ):

        self.db.delete(obj)
        self.db.commit()
