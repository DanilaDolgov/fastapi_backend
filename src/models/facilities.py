from src.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey


class FacilitiesOrm(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))


class FacilitiesRoomsOrm(Base):
    __tablename__ = "facilities_rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    facilities_id: Mapped[str] = mapped_column(ForeignKey("facilities.id"))
    rooms_id: Mapped[id] = mapped_column(ForeignKey("rooms.id"))
