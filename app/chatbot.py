import os
import re
from dotenv import load_dotenv
from groq import Groq

from app.database import (
    get_order_details,
    get_customer_by_email,
    get_customer_orders,
    update_order_status,
    create_ticket
)

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def handle_chat(user_message: str, customer_email: str = None, chat_history: list = None):
    """
    Main chatbot engine:
    1. Gathers context from the database safely.
    2. Calls Groq LLM with context.
    3. Saves the conversation into the tickets table.
    """
    if chat_history is None:
        chat_history = []

    context_info = []
    customer_id = None

    # 1. Customer Verification (if email provided)
    if customer_email:
        customer = get_customer_by_email(customer_email)
        if customer:
            customer_id = customer["customer_id"]
            orders = get_customer_orders(customer_id)
            context_info.append(f"Customer Name: {customer['name']} (ID: {customer_id})")
            context_info.append(f"Customer Order History: {orders}")

    # 2. Check if an Order ID (e.g., ORD0001) is mentioned in the message
    order_match = re.search(r"ORD\d+", user_message.upper())
    if order_match:
        order_id = order_match.group()
        order = get_order_details(order_id)
        if order:
            context_info.append(f"Order Details for {order_id}: {order}")
        else:
            context_info.append(f"Order {order_id} was not found in the database.")

    # 3. Safe Action: Handle Order Cancellation confirmation
    msg_lower = user_message.lower()
    if "cancel order" in msg_lower and order_match:
        order_id = order_match.group()
        # Require explicit confirmation
        if "confirm" in msg_lower or "yes" in msg_lower:
            update_order_status(order_id, "Cancelled")
            context_info.append(f"SYSTEM ALERT: Order {order_id} has now been CANCELLED in the database.")
        else:
            context_info.append(f"SYSTEM ALERT: Order cancellation requested for {order_id}. You MUST ask the customer for explicit confirmation before proceeding.")

    # 4. Construct System Prompt with Database Context
    system_prompt = """
    You are an AI Customer Support Specialist for an e-commerce company.
    - Be professional, polite, and helpful.
    - Only answer based on the provided Database Context below.
    - Never invent, assume, or hallucinate order or refund info.
    - If cancelling an order, require the customer to say 'confirm' before proceeding.
    """

    if context_info:
        system_prompt += "\n\nDATABASE CONTEXT:\n" + "\n".join(context_info)

    # 5. Build message payload for Groq
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_history[-4:])  # keep last 4 messages for conversational context
    messages.append({"role": "user", "content": user_message})

    # 6. Call Groq API
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=messages,
        temperature=0.3,
        max_tokens=300
    )
    reply = response.choices[0].message.content

    # 7. Audit Log: Save this conversation into the 'tickets' table
    ticket_id = create_ticket(
        customer_id=customer_id,
        message=user_message,
        chatbot_response=reply,
        status="Open" if "damage" in msg_lower or "refund" in msg_lower else "Resolved"
    )

    return {
        "reply": reply,
        "ticket_id": ticket_id
    }