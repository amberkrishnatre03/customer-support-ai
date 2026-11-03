# 🎧 AI-Powered Customer Support & Analytics System

[![Live Demo](https://img.shields.io/badge/Live_Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://customer-support-ai.onrender.com)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech)
[![Groq AI](https://img.shields.io/badge/Groq_API-gpt--oss--20b-F55036?style=for-the-badge)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

A full-stack customer support and management system built with **FastAPI**, **PostgreSQL (Neon)**, **Groq LLM (`openai/gpt-oss-20b`)**, and **Streamlit**. Fully containerized with **Docker** and deployed on **Render**.

---

## 🚀 Live Demo

* **Live Application:** (https://customer-support-ai.onrender.com)
* **Interactive API Docs (Swagger):** `http://localhost:8000/docs` (when running locally)

---

## 📌 What This Project Does

### 1. Relational Database with Raw SQL (`app/database.py`)
* Built with **Neon PostgreSQL** and **psycopg 3** (no ORM).
* Uses 4 relational tables:
  * `customers`: Stores customer identity (name, email, phone).
  * `products`: Stores product catalog, prices, and stock inventory.
  * `orders`: Links customers to products with order status (`Delivered`, `Shipped`, `Pending`, `Cancelled`).
  * `tickets`: Stores support conversations and audit logs.
* Demonstrates **SQL `JOIN`s** across orders, customers, and products, with **parameterized queries (`%s`)** to prevent SQL injection.

### 2. FastAPI REST API (`app/main.py`)
* Endpoints for viewing and managing data:
  * `GET /orders` & `GET /orders/{order_id}` — View order details.
  * `PATCH /orders/{order_id}/status` — Update order status.
  * `GET /customers`, `POST /customers`, & `PUT /customers/{customer_id}` — CRUD customer records.
  * `GET /products` — View catalog inventory.
  * `GET /tickets` — View all support tickets.
  * `POST /chat` — AI chatbot support endpoint.

### 3. AI Support Chatbot with Groq (`app/chatbot.py`)
* Uses **Groq API** running `openai/gpt-oss-20b`.
* **Zero Arbitrary SQL:** The LLM does not write SQL. The backend queries PostgreSQL for customer orders and passes verified context into the prompt.
* **Sensitive Action Guardrail:** Requires customer confirmation before cancelling any order.
* **Audit Trail:** Every customer conversation is automatically logged to the `tickets` table with `Open` or `Resolved` status.

### 4. Streamlit Admin Dashboard (`app/dashboard.py`)
* **Overview & Analytics:**
  * KPI summary cards: Total Customers, Products, Orders, and Gross Revenue.
  * Interactive category dropdown filter.
  * Order Status distribution chart (Plotly Donut).
  * Top selling products by revenue (Plotly Bar chart).
  * Warehouse stock level monitor.
  * Support ticket resolution health chart.
  * Top 5 customers by total spend.
* **Customer Support Chat:** Live chat UI where users can enter their email and ask questions about their orders.
* **Orders Management:** Table of all orders with a form to update order statuses.
* **Customers Management:** Table of customers with forms to register new customers or edit existing profiles.
* **Products & Tickets:** Clean tabular views of inventory and audit logs.

---

## 🏗️ Architecture

```text
 Browser (User / Support Admin)
        │
        ▼
 Streamlit Frontend (Port 8501)
        │
        ▼ HTTP REST
 FastAPI Backend (Port 8000)
        ├──► Groq API (openai/gpt-oss-20b)
        │
        └──► psycopg 3 (Raw SQL)
                 │
                 ▼
          Neon PostgreSQL
          ├── customers
          ├── products
          ├── orders
          └── tickets