from sqlalchemy.orm import Mapped

from app.models.base import Base


class CategoriesORM(Base):
    __tablename__ = "categories"

    name: Mapped[str]
