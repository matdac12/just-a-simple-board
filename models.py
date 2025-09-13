from sqlalchemy import Integer, String, Text, ForeignKey, DateTime, Boolean, Index
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from db import Base

class Board(Base):
    __tablename__ = "boards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    columns = relationship("ColumnModel", back_populates="board", cascade="all, delete-orphan", order_by="ColumnModel.position")

class ColumnModel(Base):
    __tablename__ = "columns"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    position: Mapped[int] = mapped_column(Integer, default=0)
    board = relationship("Board", back_populates="columns")
    cards = relationship(
        "Card", back_populates="column",
        cascade="all, delete-orphan",
        primaryjoin="and_(Card.column_id==ColumnModel.id, Card.parent_id==None)",
        order_by="Card.position"
    )

class Card(Base):
    __tablename__ = "cards"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    column_id: Mapped[int] = mapped_column(ForeignKey("columns.id", ondelete="CASCADE"), index=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)  # Index for search
    notes: Mapped[str] = mapped_column(Text, default="")
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)  # Index for due date queries
    position: Mapped[int] = mapped_column(Integer, default=0, index=True)  # Index for ordering

    column = relationship("ColumnModel", back_populates="cards")
    children = relationship("Card", cascade="all, delete-orphan",
                          backref="parent", remote_side=[id],
                          order_by="Card.position", single_parent=True)
    checklist = relationship("ChecklistItem", back_populates="card", cascade="all, delete-orphan", order_by="ChecklistItem.position")

    # Composite indexes for better query performance
    __table_args__ = (
        Index('idx_card_column_parent_position', 'column_id', 'parent_id', 'position'),
        Index('idx_card_due_date_column', 'due_at', 'column_id'),
    )

class ChecklistItem(Base):
    __tablename__ = "checklist_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(String(300))
    done: Mapped[bool] = mapped_column(Boolean, default=False, index=True)  # Index for filtering
    position: Mapped[int] = mapped_column(Integer, default=0, index=True)  # Index for ordering
    card = relationship("Card", back_populates="checklist")

    # Composite index for better query performance
    __table_args__ = (
        Index('idx_checklist_card_position', 'card_id', 'position'),
        Index('idx_checklist_card_done', 'card_id', 'done'),
    )
