from fastapi import FastAPI, HTTPException
import httpx
import os
from .models import Order, OrderCreate, OrderItem

app = FastAPI(
    title="Order Service",
    description="Microservice for managing customer orders",
    version="1.0.0"
)

# Use service names in Kubernetes deployments and localhost in local development environments
BOOK_SERVICE_URL = os.getenv("BOOK_SERVICE_URL", "http://localhost:8001")
print(f"DEBUG: BOOK_SERVICE_URL = {BOOK_SERVICE_URL}")

# In-memory storage for orders
orders_db = []
next_order_id = 1


@app.post("/orders/", response_model=Order)
async def create_order(order_create: OrderCreate):
    """Create a new order"""
    global next_order_id

    print(f"Creating order with items: {order_create.items}")

    # Validate order items
    if not order_create.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    # Call book service to check and deduct stock for each item
    async with httpx.AsyncClient() as client:
        for item in order_create.items:
            try:
                print(f"Processing book {item.book_id}, quantity {item.quantity}")

                # First check if book exists
                print(f"Calling {BOOK_SERVICE_URL}/books/{item.book_id}")
                book_response = await client.get(f"{BOOK_SERVICE_URL}/books/{item.book_id}")
                print(f"Book check response status: {book_response.status_code}")

                if book_response.status_code != 200:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Book {item.book_id} not found"
                    )

                # Try to deduct stock
                print(f"Calling deduct-stock for book {item.book_id}")
                deduct_response = await client.post(
                    f"{BOOK_SERVICE_URL}/books/{item.book_id}/deduct-stock",
                    json={"quantity": item.quantity}
                )
                print(f"Deduct stock response status: {deduct_response.status_code}")
                print(f"Deduct stock response body: {deduct_response.text}")

                if deduct_response.status_code != 200:
                    raise HTTPException(
                        status_code=409,
                        detail=f"Insufficient stock for book {item.book_id}. {deduct_response.json().get('detail', '')}"
                    )

            except httpx.ConnectError as e:
                print(f"DEBUG: Connection error: {e}")
                raise HTTPException(
                    status_code=503,
                    detail="Book service is unavailable. Please try again later."
                )
            except Exception as e:
                print(f"DEBUG: Other error: {e}")
                raise

    # Create the order
    new_order = Order(
        id=next_order_id,
        items=order_create.items,
        status="completed",
        total_amount=calculate_total_amount(order_create.items)
    )

    orders_db.append(new_order)
    next_order_id += 1

    print(f"DEBUG: Order created successfully: {new_order.id}")
    return new_order


def calculate_total_amount(items: list[OrderItem]) -> float:
    """Simplified total calculation"""
    return sum(item.quantity * 29.99 for item in items)


@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: int):
    """Get order details by ID"""
    if order_id < 1 or order_id > len(orders_db):
        raise HTTPException(status_code=404, detail="Order not found")
    return orders_db[order_id - 1]


@app.get("/orders/", response_model=list[Order])
async def list_orders():
    """List all orders"""
    return orders_db


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)