
# src/models/schemas.py

from pydantic import BaseModel
from typing   import List
from uuid     import UUID


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    reply: str


class OrderItemInput(BaseModel):
    menu_item_id : UUID
    quantity     : int


class OrderRequest(BaseModel):
    customer_name : str
    items         : List[OrderItemInput]


class OrderItemResponse(BaseModel):
    menu_item_id : UUID
    item_name    : str
    quantity     : int
    unit_price   : float


class OrderResponse(BaseModel):
    order_id      : UUID
    customer_name : str
    status        : str
    total_price   : float
    items         : List[OrderItemResponse]


class OrderStatusResponse(BaseModel):
    order_id : UUID
    status   : str
    message  : str


class MenuItemResponse(BaseModel):
    menu_item_id : UUID
    name         : str
    description  : str
    price        : float
    stock        : int


class OrderDetails(BaseModel):
    item     : str
    quantity : int
    price    : float




