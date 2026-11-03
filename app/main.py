from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.chatbot import handle_chat

from app.database import (
    get_all_customers,
    get_all_products,
    get_order_details,
    get_customer_orders,
    update_order_status,
    get_all_tickets,
    get_all_orders,
    update_customer
)

app = FastAPI(title="AI-Powered Customer Support Management System")


# Request model for updating an order status
class StatusUpdate(BaseModel):
    status: str

class ChatMessage(BaseModel):
    message: str
    customer_email: str | None = None
    chat_history: list = []

# --------------------------------------------------
# API ENDPOINTS
# --------------------------------------------------

@app.get("/")
def home():
    """Health check endpoint."""
    return {"status": "running", "message": "Customer Support API is online!"}


@app.get("/customers")
def list_customers():
    """Get all customers."""
    return get_all_customers()

class CustomerUpdate(BaseModel):
    name: str
    email: str
    phone: str | None = None


@app.put("/customers/{customer_id}")
def edit_customer(customer_id: str, payload: CustomerUpdate):
    """Update an existing customer's details."""
    updated = update_customer(customer_id, payload.name, payload.email, payload.phone)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} not found")
    return {"message": f"Customer {customer_id} updated successfully", "customer": updated}

@app.get("/products")
def list_products():
    """Get all products in the catalog."""
    return get_all_products()

@app.get("/orders")
def list_orders():
    """Get all orders for the dashboard."""
    return get_all_orders()

@app.get("/orders/{order_id}")
def read_order(order_id: str):
    """Get detailed order info including customer and product details."""
    order = get_order_details(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return order


@app.get("/customers/{customer_id}/orders")
def read_customer_orders(customer_id: str):
    """Get all orders belonging to a specific customer."""
    return get_customer_orders(customer_id)


@app.patch("/orders/{order_id}/status")
def change_order_status(order_id: str, payload: StatusUpdate):
    """Update order status (e.g., to 'Cancelled' or 'Delivered')."""
    success = update_order_status(order_id, payload.status)
    if not success:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return {"message": f"Order {order_id} status updated to {payload.status}"}


@app.get("/tickets")
def list_tickets():
    """Get all support tickets for admin review."""
    return get_all_tickets()

@app.post("/chat")
def chat(payload: ChatMessage):
    """Customer Support Chatbot endpoint."""
    result = handle_chat(
        user_message=payload.message,
        customer_email=payload.customer_email,
        chat_history=payload.chat_history
    )
    return result