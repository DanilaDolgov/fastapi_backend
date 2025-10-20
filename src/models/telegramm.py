from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base

class TelegrammChatOrm(Base):
    __tablename__ = "telegramm"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
