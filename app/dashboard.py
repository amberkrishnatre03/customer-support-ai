import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# URL for our FastAPI backend
API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Customer Support Management System",
    page_icon="🎧",
    layout="wide"
)

st.title("🎧 AI-Powered Customer Support System")


# Navigation Menu on Sidebar
page = st.sidebar.radio(
    "Navigation",
    ["Overview & Analytics", "Customer Support Chat", "Orders Management", "Customers", "Products", "Support Tickets"]
)

# --------------------------------------------------
# 1. OVERVIEW & ANALYTICS
# --------------------------------------------------
# --------------------------------------------------
# 1. OVERVIEW & ANALYTICS
# --------------------------------------------------
if page == "Overview & Analytics":
    st.header("📊 Business & Support Analytics")

    try:
        # Fetch fresh data from FastAPI
        orders = requests.get(f"{API_URL}/orders").json()
        customers = requests.get(f"{API_URL}/customers").json()
        products = requests.get(f"{API_URL}/products").json()
        tickets = requests.get(f"{API_URL}/tickets").json()

        df_orders = pd.DataFrame(orders)
        df_products = pd.DataFrame(products)
        df_tickets = pd.DataFrame(tickets)

        if not df_orders.empty:
            df_orders["total_amount"] = df_orders["total_amount"].astype(float)

        # --------------------------------------------------
        # Top KPI Metric Cards
        # --------------------------------------------------
        total_rev = df_orders["total_amount"].sum() if not df_orders.empty else 0
        open_tickets = (df_tickets["status"] == "Open").sum() if not df_tickets.empty else 0

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Customers", len(customers))
        c2.metric("Total Products", len(products))
        c3.metric("Total Orders", len(orders))
        c4.metric("Total Revenue", f"${total_rev:,.2f}")

        st.divider()

        # --------------------------------------------------
        # Interactive Filter (Select Category)
        # --------------------------------------------------
        categories = ["All"] + sorted(list(df_orders["category"].unique())) if not df_orders.empty else ["All"]
        selected_cat = st.selectbox("🔍 Filter Data by Product Category:", categories)

        # Filter dataframe based on user selection
        filtered_orders = df_orders if selected_cat == "All" else df_orders[df_orders["category"] == selected_cat]

        # --------------------------------------------------
        # Row 1: Order Status & Top Selling Products
        # --------------------------------------------------
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            st.subheader("Order Status Distribution")
            fig_status = px.pie(
                filtered_orders,
                names="status",
                hole=0.45,
                color="status",
                color_discrete_map={
                    "Delivered": "#22A06B",
                    "Shipped": "#2E86DE",
                    "Pending": "#F39C12",
                    "Cancelled": "#E74C3C"
                }
            )
            st.plotly_chart(fig_status, use_container_width=True)

        with row1_col2:
            st.subheader("Top Products by Revenue")
            top_products = (
                filtered_orders.groupby("product_name")["total_amount"]
                .sum()
                .reset_index()
                .sort_values(by="total_amount", ascending=True)
            )
            fig_prod = px.bar(
                top_products,
                x="total_amount",
                y="product_name",
                orientation="h",
                labels={"total_amount": "Revenue ($)", "product_name": "Product"},
                color="total_amount",
                color_continuous_scale="Blues"
            )
            st.plotly_chart(fig_prod, use_container_width=True)

        st.divider()

        # --------------------------------------------------
        # Row 2: Warehouse Stock & Support Ticket Health
        # --------------------------------------------------
        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            st.subheader("Warehouse Inventory Stock Levels")
            fig_stock = px.bar(
                df_products,
                x="product_name",
                y="stock",
                labels={"stock": "Units in Stock", "product_name": "Product"},
                color="category"
            )
            st.plotly_chart(fig_stock, use_container_width=True)

        with row2_col2:
            st.subheader("Support Tickets (Open vs Resolved)")
            if not df_tickets.empty:
                fig_tickets = px.pie(
                    df_tickets,
                    names="status",
                    hole=0.45,
                    color="status",
                    color_discrete_map={"Resolved": "#22A06B", "Open": "#E74C3C"}
                )
                st.plotly_chart(fig_tickets, use_container_width=True)
            else:
                st.info("No support tickets yet.")

        st.divider()

        # --------------------------------------------------
        # Row 3: Top 5 VIP Customers by Spend
        # --------------------------------------------------
        st.subheader("Top 5 Customers by Total Spend (Customer LTV)")
        top_cust = (
            df_orders.groupby("customer_name")["total_amount"]
            .sum()
            .reset_index()
            .sort_values(by="total_amount", ascending=False)
            .head(5)
        )
        fig_cust = px.bar(
            top_cust,
            x="customer_name",
            y="total_amount",
            labels={"total_amount": "Total Spend ($)", "customer_name": "Customer Name"},
            color="total_amount",
            color_continuous_scale="Greens"
        )
        st.plotly_chart(fig_cust, use_container_width=True)

    except Exception as e:
        st.error(f"Cannot connect to FastAPI backend: {e}. Make sure uvicorn is running!")

# --------------------------------------------------
# 2. CHATBOT INTERFACE
# --------------------------------------------------
elif page == "Customer Support Chat":
    st.header("💬 AI Customer Support Assistant")
    st.caption("Powered by Groq LLM & PostgreSQL")

    # Customer Email for Verification
    cust_email = st.text_input("Enter Customer Email for Verification:", value="alice@example.com")

    # Session State to store conversation
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Show past messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat Input
    user_input = st.chat_input("Type your question here (e.g., 'Where is my order ORD0001?')...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("AI is checking database..."):
                try:
                    res = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "message": user_input,
                            "customer_email": cust_email,
                            "chat_history": st.session_state.messages
                        }
                    ).json()

                    reply = res.get("reply", "No response from server.")
                    ticket_id = res.get("ticket_id")

                    st.write(reply)
                    if ticket_id:
                        st.caption(f"🎫 Logged as Support Ticket #{ticket_id}")

                    st.session_state.messages.append({"role": "assistant", "content": reply})

                except Exception as e:
                    st.error(f"Error calling chatbot: {e}")

# --------------------------------------------------
# 3. ORDERS MANAGEMENT
# --------------------------------------------------
elif page == "Orders Management":
    st.header("📦 Orders Management")
    orders = requests.get(f"{API_URL}/orders").json()
    st.dataframe(pd.DataFrame(orders), use_container_width=True)

    st.subheader("Update Order Status")
    with st.form("status_update_form"):
        target_order = st.text_input("Order ID:", value="ORD0005")
        new_status = st.selectbox("New Status:", ["Pending", "Shipped", "Delivered", "Cancelled"])
        submit_btn = st.form_submit_button("Update Status")

        if submit_btn:
            resp = requests.patch(f"{API_URL}/orders/{target_order}/status", json={"status": new_status})
            if resp.status_code == 200:
                st.success(f"Order {target_order} updated to {new_status}!")
                st.rerun()
            else:
                st.error("Failed to update order.")

# --------------------------------------------------
# 4. CUSTOMERS (Full View & Admin Editing)
# --------------------------------------------------
elif page == "Customers":
    st.header("👥 Customers Management")

    customers = requests.get(f"{API_URL}/customers").json()
    df_cust = pd.DataFrame(customers)
    st.dataframe(df_cust, use_container_width=True)

    c1, c2 = st.columns(2)

    # Box 1: Register New Customer
    with c1:
        st.subheader("➕ Register New Customer")
        with st.form("new_customer_form"):
            new_name = st.text_input("Full Name:")
            new_email = st.text_input("Email Address:")
            new_phone = st.text_input("Phone Number:", value="+1-555-0199")
            submit_new = st.form_submit_button("Register Customer")

            if submit_new:
                if new_name and new_email:
                    res = requests.post(f"{API_URL}/customers", json={"name": new_name, "email": new_email, "phone": new_phone})
                    if res.status_code == 200:
                        st.success(f"Customer {new_name} added!")
                        st.rerun()
                    else:
                        st.error("Email already exists or invalid data.")

    # Box 2: Edit Existing Customer (Internal Admin Tool)
    with c2:
        st.subheader("🛠️ Admin: Edit Customer Profile")
        if not df_cust.empty:
            cust_options = {f"{row['name']} ({row['customer_id']})": row for _, row in df_cust.iterrows()}
            selected_label = st.selectbox("Select Customer to Edit:", list(cust_options.keys()))
            selected_data = cust_options[selected_label]

            with st.form("edit_customer_form"):
                edit_name = st.text_input("Edit Name:", value=selected_data["name"])
                edit_email = st.text_input("Edit Email:", value=selected_data["email"])
                edit_phone = st.text_input("Edit Phone:", value=selected_data["phone"])
                submit_edit = st.form_submit_button("Save Changes to Database")

                if submit_edit:
                    target_id = selected_data["customer_id"]
                    res = requests.put(
                        f"{API_URL}/customers/{target_id}",
                        json={"name": edit_name, "email": edit_email, "phone": edit_phone}
                    )
                    if res.status_code == 200:
                        st.success(f"Updated {target_id} successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update customer.")

# --------------------------------------------------
# 5. PRODUCTS
# --------------------------------------------------
elif page == "Products":
    st.header("🏷️ Product Catalog")
    products = requests.get(f"{API_URL}/products").json()
    st.dataframe(pd.DataFrame(products), use_container_width=True)

# --------------------------------------------------
# 6. SUPPORT TICKETS
# --------------------------------------------------
elif page == "Support Tickets":
    st.header("🎫 Support Tickets (Audit Logs)")
    tickets = requests.get(f"{API_URL}/tickets").json()
    st.dataframe(pd.DataFrame(tickets), use_container_width=True)