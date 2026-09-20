from fastapi import FastAPI, HTTPException
from .models import Book, StockDeductionRequest

app = FastAPI(
    title="Book Service",
    description="Microservice for managing book inventory",
    version="1.0.0"
)

# In-memory database simulation
books_db = {
    1: {"title": "The Phoenix Project", "author": "Gene Kim", "stock": 10},
    2: {"title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "stock": 5},
    3: {"title": "Clean Architecture", "author": "Robert C. Martin", "stock": 8},
}


@app.get("/books/{book_id}", response_model=Book)
async def get_book(book_id: int):
    """Get book details by ID"""
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")
    return Book(id=book_id, **books_db[book_id])


@app.get("/books/", response_model=list[Book])
async def list_books():
    """List all books"""
    return [Book(id=book_id, **book_data) for book_id, book_data in books_db.items()]


@app.post("/books/{book_id}/deduct-stock")
async def deduct_stock(book_id: int, request: StockDeductionRequest):
    """Deduct stock for a book (internal API for order service)"""
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")

    current_stock = books_db[book_id]["stock"]
    if current_stock < request.quantity:
        raise HTTPException(
            status_code=409,
            detail=f"Insufficient stock. Available: {current_stock}, Requested: {request.quantity}"
        )

    # Deduct the stock
    books_db[book_id]["stock"] -= request.quantity
    return {
        "message": f"Successfully deducted {request.quantity} items",
        "remaining_stock": books_db[book_id]["stock"]
    }


@app.post("/books/{book_id}/restore-stock")
async def restore_stock(book_id: int, request: StockDeductionRequest):
    """Restore stock (for testing purposes)"""
    if book_id not in books_db:
        raise HTTPException(status_code=404, detail="Book not found")

    books_db[book_id]["stock"] += request.quantity
    return {
        "message": f"Successfully restored {request.quantity} items",
        "current_stock": books_db[book_id]["stock"]
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)