from datetime import datetime
from sqlalchemy import (
    String, Integer, ForeignKey, DateTime, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


class Book(Base):
    __tablename__ = "books"

    __table_args__ = (
        CheckConstraint("total_copies >= 1"),
        CheckConstraint("available_copies >= 0"),
        CheckConstraint("available_copies <= total_copies"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(150))
    total_copies: Mapped[int] = mapped_column(Integer, default=1)
    available_copies: Mapped[int] = mapped_column(Integer, default=1)

    borrow_records: Mapped[list["BorrowRecord"]] = relationship(
        back_populates="book"
    )


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True
    )

    borrow_records: Mapped[list["BorrowRecord"]] = relationship(
        back_populates="member"
    )


class BorrowRecord(Base):
    __tablename__ = "borrow_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id"), index=True
    )
    member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id"), index=True
    )
    status: Mapped[str] = mapped_column(
        String(20), default="borrowed"
    )
    borrowed_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )
    returned_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    book: Mapped["Book"] = relationship(
        back_populates="borrow_records"
    )
    member: Mapped["Member"] = relationship(
        back_populates="borrow_records"
    )
