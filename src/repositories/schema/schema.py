
# src/repositories/schema/schema.py

import uuid
from sqlalchemy import Column, String, Numeric, Boolean, Integer,text, Text, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
# from repositories.Database import Base
# from sqlalchemy.orm import DeclarativeBase
from repositories.Database import Base



# TABLE 1 — menu_items


class MenuItem(Base):
    __tablename__ = "menu_items"

    menu_item_id  = Column(UUID(as_uuid=True), primary_key=True,  default=uuid.uuid4)
    name          = Column(String(100),         nullable=False)
    description   = Column(Text,                nullable=True)
    price         = Column(Numeric(10, 2),       nullable=False)
    stock         = Column(Integer,              nullable=False,  default=0)
    is_available  = Column(Boolean,              default=True,    nullable=False)
    created_at    = Column(TIMESTAMP,            server_default=func.now(), nullable=False)
    created_by    = Column(String(100),          nullable=True,   default="SYSTEM")
    updated_at    = Column(TIMESTAMP,            server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by    = Column(String(100),          nullable=True)

    order_items   = relationship("OrderItem", back_populates="menu_item")



# TABLE 2 — orders


class Order(Base):
    __tablename__ = "orders"

    order_id     = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name         = Column(String(100),         nullable=False)
    order_code   = Column(String(10),          nullable=False,  unique=True)
    status       = Column(Enum("pending","preparing","ready","picked_up",name="order_status_enum"),nullable=False,default="pending" )
    total_price  = Column(Numeric(10, 2),nullable=False)
    is_available = Column(Boolean,default=True,    nullable=False)
    created_at   = Column(TIMESTAMP,server_default=func.now(), nullable=False)
    created_by   = Column(String(100),nullable=True,   default="SYSTEM")
    updated_at   = Column(TIMESTAMP,server_default=func.now(), onupdate=func.now(), nullable=False)
    updated_by   = Column(String(100),          nullable=True)

    order_items  = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")



# TABLE 3 — order_items


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(UUID(as_uuid=True), primary_key=True,                                       default=uuid.uuid4)
    order_id      = Column(UUID(as_uuid=True), ForeignKey("orders.order_id"),         nullable=False)
    item_id       = Column(UUID(as_uuid=True), ForeignKey("menu_items.menu_item_id"), nullable=False)
    quantity      = Column(Integer,             nullable=False)
    price         = Column(Numeric(10, 2),       nullable=False)
    is_available  = Column(Boolean,              default=True,                         nullable=False)
    created_at    = Column(TIMESTAMP,            server_default=func.now(),            nullable=False)
    created_by    = Column(String(100),          nullable=True,                        default="SYSTEM")
    updated_at    = Column(TIMESTAMP,            server_default=func.now(),            onupdate=func.now(), nullable=False)
    updated_by    = Column(String(100),          nullable=True)

    order         = relationship("Order",    back_populates="order_items")
    menu_item     = relationship("MenuItem", back_populates="order_items")



# table -4 Error Logs

class ErrorLog(Base):
    __tablename__ = "error_logs"

    error_id      = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name     = Column(Text,nullable=True)
    function_name = Column(Text, nullable=True)
    error_message = Column(Text,nullable=True)
    is_active     = Column(Boolean,nullable=False, server_default=text("TRUE"), default=True)
    created_at    = Column(TIMESTAMP,          nullable=False, server_default=func.now())
    created_by    = Column(String(50),         nullable=False, server_default=text("'SYSTEM'"), default="SYSTEM")
    updated_at    = Column(TIMESTAMP,          nullable=True,  onupdate=func.now())
    updated_by    = Column(String(50),         nullable=True)

