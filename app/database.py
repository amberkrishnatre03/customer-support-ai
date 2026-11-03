import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    """Helper to connect to Neon PostgreSQL."""
    return psycopg.connect(DATABASE_URL)


# --------------------------------------------------
# 1. CUSTOMER OPERATIONS
# --------------------------------------------------

def get_customer_by_email(email: str):
    """Find a customer by email (used by Chatbot for verification)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT customer_id, name, email, phone 
                FROM customers 
                WHERE LOWER(email) = LOWER(%s);
            """, (email,))
            row = cur.fetchone()
            if row:
                return {"customer_id": row[0], "name": row[1], "email": row[2], "phone": row[3]}
            return None


def update_customer(customer_id: str, name: str, email: str, phone: str = None):
    """Update an existing customer's contact details."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE customers 
                SET name = %s, email = %s, phone = %s
                WHERE customer_id = %s
                RETURNING customer_id, name, email, phone;
            """, (name, email, phone, customer_id))
            row = cur.fetchone()
            if row:
                return {"customer_id": row[0], "name": row[1], "email": row[2], "phone": row[3]}
            return None

def get_all_customers():
    """Retrieve all customers for the dashboard."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT customer_id, name, email, phone FROM customers ORDER BY customer_id;")
            columns = ["customer_id", "name", "email", "phone"]
            return [dict(zip(columns, row)) for row in cur.fetchall()]


# --------------------------------------------------
# 2. ORDER OPERATIONS (With SQL Joins)
# --------------------------------------------------


def get_all_orders():
    """Retrieve all orders with customer and product details for analytics."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT o.order_id, c.name AS customer_name, p.product_name, p.category, o.quantity, o.total_amount, o.status, o.order_date
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN products p ON o.product_id = p.product_id
                ORDER BY o.order_date DESC;
            """)
            cols = ["order_id", "customer_name", "product_name", "category", "quantity", "total_amount", "status", "order_date"]
            return [dict(zip(cols, row)) for row in cur.fetchall()]



def get_order_details(order_id: str):
    """
    Look up an order by its ID.
    Demonstrates SQL JOIN across orders, customers, and products!
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    o.order_id,
                    c.name AS customer_name,
                    c.email AS customer_email,
                    p.product_name,
                    o.quantity,
                    o.total_amount,
                    o.status,
                    o.order_date
                FROM orders o
                JOIN customers c ON o.customer_id = c.customer_id
                JOIN products p ON o.product_id = p.product_id
                WHERE UPPER(o.order_id) = UPPER(%s);
            """, (order_id,))
            row = cur.fetchone()
            if row:
                cols = ["order_id", "customer_name", "customer_email", "product_name", "quantity", "total_amount", "status", "order_date"]
                return dict(zip(cols, row))
            return None


def get_customer_orders(customer_id: str):
    """Get all orders belonging to a customer."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT o.order_id, p.product_name, o.quantity, o.total_amount, o.status, o.order_date
                FROM orders o
                JOIN products p ON o.product_id = p.product_id
                WHERE o.customer_id = %s
                ORDER BY o.order_date DESC;
            """, (customer_id,))
            cols = ["order_id", "product_name", "quantity", "total_amount", "status", "order_date"]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


def update_order_status(order_id: str, new_status: str):
    """Update order status (e.g., Cancelled or Delivered)."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE orders 
                SET status = %s 
                WHERE UPPER(order_id) = UPPER(%s)
                RETURNING order_id, status;
            """, (new_status, order_id))
            return cur.fetchone() is not None


# --------------------------------------------------
# 3. PRODUCT OPERATIONS
# --------------------------------------------------

def get_all_products():
    """Retrieve catalog products."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT product_id, product_name, category, price, stock FROM products ORDER BY product_id;")
            cols = ["product_id", "product_name", "category", "price", "stock"]
            return [dict(zip(cols, row)) for row in cur.fetchall()]


# --------------------------------------------------
# 4. TICKET OPERATIONS (Audit Logs)
# --------------------------------------------------

def create_ticket(customer_id: str, message: str, chatbot_response: str, status: str = "Resolved"):
    """Save a support interaction into the tickets audit log."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tickets (customer_id, message, chatbot_response, status)
                VALUES (%s, %s, %s, %s)
                RETURNING ticket_id;
            """, (customer_id, message, chatbot_response, status))
            return cur.fetchone()[0]


def get_all_tickets():
    """Retrieve support tickets for the dashboard."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT t.ticket_id, c.name AS customer_name, t.message, t.chatbot_response, t.status, t.created_at
                FROM tickets t
                LEFT JOIN customers c ON t.customer_id = c.customer_id
                ORDER BY t.created_at DESC;
            """)
            cols = ["ticket_id", "customer_name", "message", "chatbot_response", "status", "created_at"]
            return [dict(zip(cols, row)) for row in cur.fetchall()]