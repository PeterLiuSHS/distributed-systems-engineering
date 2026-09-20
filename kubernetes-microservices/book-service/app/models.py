from pydantic import BaseModel

class Book(BaseModel):
    id: int
    title: str
    author: str
    stock: int

class StockDeductionRequest(BaseModel):
    quantity: int = 1