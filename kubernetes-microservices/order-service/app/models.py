from pydantic import BaseModel
from typing import List

class OrderItem(BaseModel):
    book_id: int
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItem]

class Order(OrderCreate):
    id: int
    status: str = "created"
    total_amount: float = 0.0  # Simplified