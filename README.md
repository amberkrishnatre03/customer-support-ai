# 🎧 AI-Powered Customer Support & Analytics System

[![Live Demo](https://img.shields.io/badge/Live_Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://customer-support-ai.onrender.com)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech)
[![Groq AI](https://img.shields.io/badge/Groq_API-gpt--oss--20b-F55036?style=for-the-badge)](https://groq.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

An end-to-end intelligent customer operations and analytics platform. Built with a normalized **PostgreSQL** relational database, a **FastAPI** backend, a **Groq LLM support agent**, and an interactive **Streamlit & Plotly** executive analytics dashboard — containerized with **Docker** and deployed live on **Render**.

---

## 🚀 Live Demo

* **Web Application:** [https://customer-support-ai.onrender.com](https://customer-support-ai.onrender.com)
* **Interactive API Docs (Swagger):** `https://customer-support-ai.onrender.com/docs`

---

## 🌟 Key Highlights & Capabilities

### 1. Relational Data Architecture (Neon PostgreSQL)
* Normalized 4-table relational database (`customers`, `products`, `orders`, `tickets`) enforcing strict primary key, foreign key, and `TIMESTAMPTZ` (UTC) referential integrity.
* Raw SQL access layer implemented with **psycopg 3**, utilizing parameterized queries (`%s`) to protect against SQL injection vulnerabilities.
* Multi-table relational SQL `JOIN`s to aggregate orders, catalog items, and customer profiles into unified records.

### 2. Context-Aware AI Support Agent (Groq LLM)
* Powered by Groq's high-speed inference engine using `openai/gpt-oss-20b`.
* **Zero Arbitrary SQL Execution:** Understands natural-language queries, verifies customer credentials, and fetches order context strictly through pre-authorized Python database functions.
* **Sensitive Action Guardrails:** Requires explicit customer confirmation before triggering mutations (such as order cancellations).
* **Automated Audit Logging:** Every customer interaction is automatically written to the `tickets` table with status tracking (`Open` vs `Resolved`).

### 3. Executive Business Intelligence & Analytics Dashboard
* **KPI Metrics:** Real-time tracking of Total Customers, Active Products, Total Orders, and Gross Revenue.
* **RFM Customer Segmentation:** Frequency vs. Monetary value scatter plot identifying VIP accounts and high-value buyers.
* **Customer 360 Inspector:** Deep-dive interface providing personalized purchase history, total orders, and Customer Lifetime Value (LTV) per client.
* **Sales Velocity Trend:** Daily revenue time-series tracking.
* **Inventory Stock Monitor:** Warehouse unit alerts across catalog categories.
* **Back-Office CRUD Tools:** Interfaces to register new customers, edit customer profiles, and update order statuses.

---

## 🏗️ System Architecture

```text
       ┌────────────────────────────────────────────────────────┐
       │               User / Support Agent                     │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼
       ┌────────────────────────────────────────────────────────┐
       │             Streamlit Dashboard (Port 8501)            │
       │   - Executive Analytics (Plotly)                       │
       │   - Customer 360 Inspector & RFM Segmentation          │
       │   - Interactive AI Support Chat UI                     │
       │   - Back-Office Order & Profile Management             │
       └──────────────────────────┬─────────────────────────────┘
                                  │
                                  ▼ REST API Calls
       ┌────────────────────────────────────────────────────────┐
       │               FastAPI Backend (Port 8000)              │
       │   - REST Endpoints (/orders, /customers, /chat)        │
       │   - Request Validation (Pydantic)                      │
       └──────────────┬──────────────────────────┬──────────────┘
                      │                          │
                      ▼                          ▼
       ┌──────────────────────────────┐ ┌──────────────────────┐
       │   Groq LLM Inference API     │ │ psycopg 3 Data Layer │
       │   - openai/gpt-oss-20b       │ │ - Parameterized SQL  │
       │   - Intent & Entity Parsing  │ │ - Relational JOINs   │
       │   - Context-Injected Prompts │ │ - ACID Transactions  │
       └──────────────┬───────────────┘ └──────────┬───────────┘
                      │                            │
                      └──────────────┬─────────────┘
                                     │
                                     ▼
       ┌────────────────────────────────────────────────────────┐
       │               Neon Serverless PostgreSQL               │
       │   ├── customers  (Customer identities & contact info)  │
       │   ├── products   (Catalog pricing & warehouse stock)   │
       │   ├── orders     (Transaction records & order status)  │
       │   └── tickets    (Audit trails & support cases)        │
       └────────────────────────────────────────────────────────┘