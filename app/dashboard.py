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

# Clean, Uncluttered 3-Page Sidebar
page = st.sidebar.radio(
    "Navigation",
    ["💬 AI Customer Support", "📊 Statistical EDA & Insights", "🛠️ Database & Operations Hub"]
)


# ==================================================
# PAGE 1: 💬 AI CUSTOMER SUPPORT (THE HERO)
# ==================================================
if page == "💬 AI Customer Support":
    st.header("💬 AI Customer Support Assistant")
    st.caption("Powered by Groq LLM (openai/gpt-oss-20b) & PostgreSQL")

    # Customer Email for Verification
    cust_email = st.text_input("Customer Email (for identity verification):", value="alice@example.com")

    # --------------------------------------------------
    # Quick Clickable Suggested Prompts
    # --------------------------------------------------
    st.write("**💡 Click a suggested question to try it instantly:**")
    prompt_to_send = None
    b1, b2, b3, b4 = st.columns(4)

    if b1.button("📦 Where is ORD0001?"):
        prompt_to_send = "Where is my order ORD0001?"
    if b2.button("📋 My Order History"):
        prompt_to_send = "Show my recent orders"
    if b3.button("❌ Cancel ORD0003"):
        prompt_to_send = "I want to cancel order ORD0003"
    if b4.button("⚠️ Damaged Item"):
        prompt_to_send = "I received a damaged product and need help"

    st.divider()

    # Session State for Conversation
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat Input Box
    user_input = st.chat_input("Type your question here...")
    active_message = user_input or prompt_to_send

    # Process Active Message
    if active_message:
        st.session_state.messages.append({"role": "user", "content": active_message})
        with st.chat_message("user"):
            st.write(active_message)

        with st.chat_message("assistant"):
            with st.spinner("AI is verifying database records..."):
                try:
                    res = requests.post(
                        f"{API_URL}/chat",
                        json={
                            "message": active_message,
                            "customer_email": cust_email,
                            "chat_history": st.session_state.messages
                        }
                    ).json()

                    reply = res.get("reply", "No response from server.")
                    ticket_id = res.get("ticket_id")

                    st.write(reply)
                    if ticket_id:
                        st.caption(f"🎫 Automatically logged to PostgreSQL as Support Ticket #{ticket_id}")

                    st.session_state.messages.append({"role": "assistant", "content": reply})

                except Exception as e:
                    st.error(f"Error communicating with AI backend: {e}")


# ==================================================
# PAGE 2: 📊 STATISTICAL EDA & INSIGHTS (DATA SCIENCE)
# ==================================================
elif page == "📊 Statistical EDA & Insights":
    st.header("📊 Exploratory Data Analysis (EDA) & Customer Intelligence")
    st.caption("Statistical distribution metrics, quartile spreads, and behavioral segmentation")

    try:
        orders = requests.get(f"{API_URL}/orders").json()
        customers = requests.get(f"{API_URL}/customers").json()
        products = requests.get(f"{API_URL}/products").json()
        tickets = requests.get(f"{API_URL}/tickets").json()

        df_orders = pd.DataFrame(orders)
        df_products = pd.DataFrame(products)
        df_tickets = pd.DataFrame(tickets)

        if not df_orders.empty:
            df_orders["total_amount"] = df_orders["total_amount"].astype(float)
            df_orders["order_date"] = pd.to_datetime(df_orders["order_date"])

        # Statistical Calculations
        total_rev = df_orders["total_amount"].sum() if not df_orders.empty else 0
        mean_spend = df_orders["total_amount"].mean() if not df_orders.empty else 0
        median_spend = df_orders["total_amount"].median() if not df_orders.empty else 0

        # Repeat Customer Rate (% with 2+ orders)
        if not df_orders.empty:
            cust_counts = df_orders["customer_name"].value_counts()
            repeat_rate = ((cust_counts > 1).sum() / len(cust_counts)) * 100
        else:
            repeat_rate = 0.0

        # Contact-to-Order Ratio (Complaint Rate)
        complaint_rate = (len(df_tickets) / len(df_orders) * 100) if len(df_orders) > 0 else 0.0

        # Top Statistical Metric Cards
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Gross Revenue", f"${total_rev:,.2f}")
        c2.metric("Mean / Median (Skewness)", f"${mean_spend:,.0f} / ${median_spend:,.0f}")
        c3.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")
        c4.metric("Support Ticket Rate", f"{complaint_rate:.1f}%")

        st.divider()

        # Master Category Filter
        categories = ["All"] + sorted(list(df_orders["category"].unique())) if not df_orders.empty else ["All"]
        selected_cat = st.selectbox("🔍 Filter EDA by Product Category:", categories)

        filtered_orders = df_orders if selected_cat == "All" else df_orders[df_orders["category"] == selected_cat]

        # ROW 1: Statistical Box Plot + Transaction Histogram
        r1_c1, r1_c2 = st.columns(2)

        with r1_c1:
            st.subheader("📦 Price Spread & Outliers by Category (Box Plot)")
            if not filtered_orders.empty:
                fig_box = px.box(
                    filtered_orders,
                    x="category",
                    y="total_amount",
                    color="category",
                    points="all",
                    labels={"total_amount": "Order Value ($)", "category": "Category"}
                )
                fig_box.update_layout(showlegend=False)
                st.plotly_chart(fig_box, use_container_width=True)

        with r1_c2:
            st.subheader("📊 Transaction Value Distribution (Histogram)")
            if not filtered_orders.empty:
                fig_hist = px.histogram(
                    filtered_orders,
                    x="total_amount",
                    nbins=12,
                    labels={"total_amount": "Order Amount ($)"},
                    color_discrete_sequence=["#2E86DE"]
                )
                fig_hist.update_layout(bargap=0.1)
                st.plotly_chart(fig_hist, use_container_width=True)

        st.divider()

        # ROW 2: Customer RFM Scatter + Bivariate Status Bar
        r2_c1, r2_c2 = st.columns(2)

        with r2_c1:
            st.subheader("🎯 Customer RFM Matrix (Frequency vs. Spend)")
            if not filtered_orders.empty:
                cust_rfm = filtered_orders.groupby("customer_name").agg(
                    total_spend=("total_amount", "sum"),
                    order_count=("order_id", "count")
                ).reset_index()

                fig_rfm = px.scatter(
                    cust_rfm,
                    x="order_count",
                    y="total_spend",
                    size="total_spend",
                    color="customer_name",
                    hover_name="customer_name",
                    labels={"order_count": "Orders Placed (Frequency)", "total_spend": "Lifetime Spend ($)"}
                )
                st.plotly_chart(fig_rfm, use_container_width=True)

        with r2_c2:
            st.subheader("🔄 Fulfillment Status by Category (Cross-Analysis)")
            if not filtered_orders.empty:
                fig_status_cat = px.histogram(
                    filtered_orders,
                    x="category",
                    color="status",
                    barmode="group",
                    color_discrete_map={
                        "Delivered": "#22A06B",
                        "Shipped": "#2E86DE",
                        "Pending": "#F39C12",
                        "Cancelled": "#E74C3C"
                    },
                    labels={"category": "Category", "count": "Orders"}
                )
                st.plotly_chart(fig_status_cat, use_container_width=True)

        # Clean Hidden Drawer for Raw Data
        with st.expander("🔍 Click to inspect raw orders dataset"):
            st.dataframe(
                df_orders[["order_id", "customer_name", "product_name", "category", "quantity", "total_amount", "status", "order_date"]],
                use_container_width=True,
                hide_index=True
            )

    except Exception as e:
        st.error(f"Cannot connect to backend: {e}")


# ==================================================
# PAGE 3: 🛠️ DATABASE & OPERATIONS HUB (ALL CRUD IN TABS)
# ==================================================
elif page == "🛠️ Database & Operations Hub":
    st.header("🛠️ Relational Database Management Hub")
    st.caption("Internal administration, CRUD operations, and live PostgreSQL audit logs")

    tab_orders, tab_customers, tab_products, tab_tickets = st.tabs([
        "📦 Orders Management",
        "👥 Customers Management",
        "🏷️ Product Catalog",
        "🎫 Support Tickets (Audit)"
    ])

    # 1. ORDERS TAB
    with tab_orders:
        orders = requests.get(f"{API_URL}/orders").json()
        st.dataframe(pd.DataFrame(orders), use_container_width=True)

        st.subheader("Update Order Status")
        with st.form("order_status_form"):
            target_order = st.text_input("Order ID:", value="ORD0005")
            new_status = st.selectbox("New Status:", ["Pending", "Shipped", "Delivered", "Cancelled"])
            if st.form_submit_button("Update Status"):
                res = requests.patch(f"{API_URL}/orders/{target_order}/status", json={"status": new_status})
                if res.status_code == 200:
                    st.success(f"Order {target_order} updated to {new_status}!")
                    st.rerun()

    # 2. CUSTOMERS TAB (View + Add + Edit)
    with tab_customers:
        customers = requests.get(f"{API_URL}/customers").json()
        df_cust = pd.DataFrame(customers)
        st.dataframe(df_cust, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("➕ Register Customer")
            with st.form("add_cust"):
                n_name = st.text_input("Name:")
                n_email = st.text_input("Email:")
                n_phone = st.text_input("Phone:", value="+1-555-0199")
                if st.form_submit_button("Add Customer"):
                    res = requests.post(f"{API_URL}/customers", json={"name": n_name, "email": n_email, "phone": n_phone})
                    if res.status_code == 200:
                        st.success("Customer added!")
                        st.rerun()

        with col2:
            st.subheader("🛠️ Edit Profile")
            if not df_cust.empty:
                cust_dict = {f"{r['name']} ({r['customer_id']})": r for _, r in df_cust.iterrows()}
                chosen_lbl = st.selectbox("Select Customer:", list(cust_dict.keys()))
                c_data = cust_dict[chosen_lbl]

                with st.form("edit_cust"):
                    e_name = st.text_input("Name:", value=c_data["name"])
                    e_email = st.text_input("Email:", value=c_data["email"])
                    e_phone = st.text_input("Phone:", value=c_data["phone"])
                    if st.form_submit_button("Save Changes"):
                        res = requests.put(f"{API_URL}/customers/{c_data['customer_id']}", json={"name": e_name, "email": e_email, "phone": e_phone})
                        if res.status_code == 200:
                            st.success("Profile updated!")
                            st.rerun()

    # 3. PRODUCTS TAB
    with tab_products:
        products = requests.get(f"{API_URL}/products").json()
        st.dataframe(pd.DataFrame(products), use_container_width=True)

    # 4. TICKETS TAB
    with tab_tickets:
        tickets = requests.get(f"{API_URL}/tickets").json()
        st.dataframe(pd.DataFrame(tickets), use_container_width=True)