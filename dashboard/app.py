import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Support Email Intelligence",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look and fluid animations
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .stMetric:hover {
        transform: translateY(-5px);
        box-shadow: 0 4px 10px rgba(88, 166, 255, 0.2);
    }
    .stTable {
        background-color: #161b22;
        border-radius: 10px;
    }
    h1, h2, h3 {
        color: #58a6ff;
    }
    .stButton>button {
        border-radius: 5px;
        width: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(88, 166, 255, 0.2);
    }
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"

def fetch_emails():
    try:
        response = requests.get(f"{API_URL}/emails")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error connecting to backend: {e}")
        return pd.DataFrame()

def update_status(email_id, status):
    requests.patch(f"{API_URL}/emails/{email_id}/status", json={"status": status})

def update_reply(email_id, reply):
    requests.patch(f"{API_URL}/emails/{email_id}/reply", json={"suggested_reply": reply})

# Title
st.title("📧 Support Email Intelligence Dashboard")

# Sidebar Navigation using buttons to act as tabs
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard Overview"

def set_page(page_name):
    st.session_state.page = page_name

st.sidebar.title("Navigation")
st.sidebar.button("Dashboard Overview", type="primary" if st.session_state.page == "Dashboard Overview" else "secondary", on_click=set_page, args=("Dashboard Overview",))
st.sidebar.button("Ticket Management", type="primary" if st.session_state.page == "Ticket Management" else "secondary", on_click=set_page, args=("Ticket Management",))
st.sidebar.button("Analytics & Insights", type="primary" if st.session_state.page == "Analytics & Insights" else "secondary", on_click=set_page, args=("Analytics & Insights",))

page = st.session_state.page

# Load data
df = fetch_emails()

if not df.empty:
    # Page-level Filters with Popover
    with st.popover("⚙️ Filter Data", icon="🔍"):
        st.markdown("**Select Filters**")
        status_filter = st.selectbox("Status", options=["All"] + list(df['status'].unique()))
        category_filter = st.selectbox("Category", options=["All"] + list(df['category'].unique()))
        priority_filter = st.selectbox("Priority", options=["All"] + list(df['priority'].unique()))

    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All":
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    if category_filter != "All":
        filtered_df = filtered_df[filtered_df['category'] == category_filter]
    if priority_filter != "All":
        filtered_df = filtered_df[filtered_df['priority'] == priority_filter]

    st.markdown("---")

    if page == "Dashboard Overview":
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Emails", len(filtered_df))
        with col2:
            st.metric("Open Tickets", len(filtered_df[filtered_df['status'] == 'Open']))
        with col3:
            st.metric("Resolved Tickets", len(filtered_df[filtered_df['status'] == 'Resolved']))
        with col4:
            st.metric("High Priority", len(filtered_df[filtered_df['priority'] == 'High']))

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Category Distribution")
            if not filtered_df.empty:
                fig_cat = px.pie(filtered_df, names='category', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                fig_cat.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
                st.plotly_chart(fig_cat, width='stretch')
            else:
                st.info("No data to display category distribution.")
            
        with c2:
            st.subheader("Priority Distribution")
            if not filtered_df.empty:
                prio_counts = filtered_df['priority'].value_counts().reset_index()
                prio_counts.columns = ['priority', 'count']
                fig_prio = px.bar(prio_counts, x='priority', y='count', 
                                  labels={'priority': 'Priority', 'count': 'Count'},
                                  color='priority', color_discrete_map={'High': '#ff4b4b', 'Medium': '#ffa500', 'Low': '#00ff00'})
                fig_prio.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
                st.plotly_chart(fig_prio, width='stretch')
            else:
                st.info("No data to display priority distribution.")

    elif page == "Ticket Management":
        # Ticket Table
        st.subheader("🎫 Recent Tickets")
        st.dataframe(filtered_df[['sender', 'subject', 'category', 'priority', 'status', 'confidence', 'created_at']], width='stretch')

        # Ticket Detail View
        st.markdown("---")
        st.subheader("📝 Ticket Detail View")
        selected_ticket_id = st.selectbox("Select a ticket to view details", options=filtered_df['id'].tolist(), format_func=lambda x: f"Ticket #{x} - {filtered_df[filtered_df['id']==x]['subject'].values[0]}" if not filtered_df[filtered_df['id']==x].empty else f"Ticket #{x}")
        
        if selected_ticket_id:
            ticket = filtered_df[filtered_df['id'] == selected_ticket_id].iloc[0]
            
            td1, td2 = st.columns([2, 1])
            
            with td1:
                st.markdown(f"**From:** {ticket['sender']}")
                st.markdown(f"**Subject:** {ticket['subject']}")
                st.markdown("**Body:**")
                st.text_area("Email Content", value=ticket['body'], height=200, disabled=True)
                
                st.markdown("**Suggested Reply:**")
                new_reply = st.text_area("Edit reply", value=ticket['suggested_reply'], height=150)
                if st.button("Save Reply"):
                    update_reply(selected_ticket_id, new_reply)
                    st.success("Reply updated!")
                    st.rerun()

            with td2:
                st.markdown(f"**Category:** `{ticket['category']}`")
                st.markdown(f"**Priority:** `{ticket['priority']}`")
                st.markdown(f"**Sentiment:** `{ticket['sentiment']}`")
                st.markdown(f"**Confidence:** `{ticket['confidence']:.2f}`")
                st.markdown(f"**Current Status:** `{ticket['status']}`")
                
                st.markdown("---")
                if st.button("Mark as Resolved"):
                    update_status(selected_ticket_id, "Resolved")
                    st.success("Ticket Resolved!")
                    st.rerun()
                
                if st.button("Mark as Pending"):
                    update_status(selected_ticket_id, "Pending")
                    st.info("Ticket Pending.")
                    st.rerun()
                
                if st.button("Mark as Open"):
                    update_status(selected_ticket_id, "Open")
                    st.warning("Ticket Open.")
                    st.rerun()

    elif page == "Analytics & Insights":
        # Emails per day
        st.subheader("📈 Emails Over Time")
        if not filtered_df.empty:
            filtered_df_copy = filtered_df.copy()
            filtered_df_copy['created_at_dt'] = pd.to_datetime(filtered_df_copy['created_at'], format='ISO8601', utc=True)
            daily_counts = filtered_df_copy.groupby(filtered_df_copy['created_at_dt'].dt.date).size().reset_index(name='count')
            fig_time = px.line(daily_counts, x='created_at_dt', y='count', markers=True, color_discrete_sequence=['#58a6ff'])
            fig_time.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0")
            st.plotly_chart(fig_time, width='stretch')
        else:
            st.info("No data to display emails over time.")

else:
    st.info("No email data found. Send some data to the API to see it here!")
    if st.button("Refresh"):
        st.rerun()
