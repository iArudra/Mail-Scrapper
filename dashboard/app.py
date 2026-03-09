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

# Custom CSS for premium look
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

# Load data
df = fetch_emails()

if not df.empty:
    # Sidebar Filters
    st.sidebar.header("Filters")
    status_filter = st.sidebar.multiselect("Status", options=df['status'].unique(), default=df['status'].unique())
    category_filter = st.sidebar.multiselect("Category", options=df['category'].unique(), default=df['category'].unique())
    priority_filter = st.sidebar.multiselect("Priority", options=df['priority'].unique(), default=df['priority'].unique())

    # Apply filters
    filtered_df = df[
        (df['status'].isin(status_filter)) &
        (df['category'].isin(category_filter)) &
        (df['priority'].isin(priority_filter))
    ]

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Emails", len(df))
    with col2:
        st.metric("Open Tickets", len(df[df['status'] == 'Open']))
    with col3:
        st.metric("Resolved Tickets", len(df[df['status'] == 'Resolved']))
    with col4:
        st.metric("High Priority", len(df[df['priority'] == 'High']))

    # Charts
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Category Distribution")
        fig_cat = px.pie(filtered_df, names='category', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_cat, width='stretch')
        
    with c2:
        st.subheader("Priority Distribution")
        prio_counts = filtered_df['priority'].value_counts().reset_index()
        prio_counts.columns = ['priority', 'count']
        fig_prio = px.bar(prio_counts, x='priority', y='count', 
                          labels={'priority': 'Priority', 'count': 'Count'},
                          color='priority', color_discrete_map={'High': '#ff4b4b', 'Medium': '#ffa500', 'Low': '#00ff00'})
        st.plotly_chart(fig_prio, width='stretch')

    # Emails per day
    st.subheader("Emails Over Time")
    filtered_df['created_at_dt'] = pd.to_datetime(filtered_df['created_at'], format='ISO8601', utc=True)
    daily_counts = filtered_df.groupby(filtered_df['created_at_dt'].dt.date).size().reset_index(name='count')
    fig_time = px.line(daily_counts, x='created_at_dt', y='count', markers=True)
    st.plotly_chart(fig_time, width='stretch')

    # Ticket Table
    st.subheader("Tickets")
    st.dataframe(filtered_df[['sender', 'subject', 'category', 'priority', 'status', 'confidence', 'created_at']], width='stretch')

    # Ticket Detail View
    st.markdown("---")
    st.subheader("Ticket Detail View")
    selected_ticket_id = st.selectbox("Select a ticket to view details", options=filtered_df['id'].tolist(), format_func=lambda x: f"Ticket #{x} - {filtered_df[filtered_df['id']==x]['subject'].values[0]}")
    
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

else:
    st.info("No email data found. Send some data to the API to see it here!")
    if st.button("Refresh"):
        st.rerun()
