"""
Complaint Management Dashboard
Admin view for department-wise complaint tracking and AI-generated summaries
"""

import streamlit as st
from datetime import datetime, timedelta
from conversation_manager import ConversationManager
from complaint_summarizer import ComplaintSummarizer
from db import engine
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Complaint Dashboard",
    page_icon="[DASHBOARD_ICON]",
    layout="wide"
)

# Initialize managers
if 'conv_manager' not in st.session_state:
    st.session_state.conv_manager = ConversationManager(engine)

if 'summarizer' not in st.session_state:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    st.session_state.summarizer = ComplaintSummarizer(GEMINI_API_KEY, GEMINI_MODEL)

# Initialize summary cache
if 'summary_cache' not in st.session_state:
    st.session_state.summary_cache = {}

st.title("[DASHBOARD] Complaint Management Dashboard")
st.caption("Department-wise complaint tracking and AI-powered analytics")

# Filters Section
st.sidebar.header("[FILTER] Filters")

departments = [
    "All Departments",
    "Network Operations",
    "Billing Department",
    "Technical Support",
    "Customer Support"
]
selected_dept = st.sidebar.selectbox("Department", departments)

# Date range filter
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("From", datetime.now() - timedelta(days=30))
with col2:
    end_date = st.date_input("To", datetime.now())

status_filter = st.sidebar.selectbox("Status", ["open", "in_progress", "resolved", "closed", "all"])

# Fetch complaints
dept_filter = None if selected_dept == "All Departments" else selected_dept
status = None if status_filter == "all" else status_filter

try:
    complaints = st.session_state.conv_manager.get_complaints_by_department(
        department=dept_filter,
        start_date=datetime.combine(start_date, datetime.min.time()),
        end_date=datetime.combine(end_date, datetime.max.time()),
        status=status
    )
except Exception as e:
    st.error(f"Error fetching complaints: {e}")
    complaints = []

# Metrics Section
st.header("[METRICS] Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Complaints", len(complaints))

with col2:
    high_priority = sum(1 for c in complaints if c[3] == 'HIGH')
    st.metric("High Priority", high_priority, delta="Urgent" if high_priority > 0 else None, delta_color="inverse")

with col3:
    open_complaints = sum(1 for c in complaints if c[5] == 'open')
    st.metric("Open Cases", open_complaints)

with col4:
    resolved = sum(1 for c in complaints if c[5] == 'resolved')
    resolution_rate = (resolved / len(complaints) * 100) if complaints else 0
    st.metric("Resolution Rate", f"{resolution_rate:.1f}%")

st.markdown("---")

# AI Summary Section
st.header("[AI] AI Executive Summary")

col1, col2 = st.columns([3, 1])
with col1:
    st.info("Generate a concise executive summary of complaints for management review (PA style)")
with col2:
    generate_btn = st.button("[GENERATE] Generate Summary", type="primary", use_container_width=True)

# Check cache
cache_key = f"{selected_dept}_{start_date}_{end_date}_{len(complaints)}"
cache_time = st.session_state.summary_cache.get(f"{cache_key}_time", 0)
is_cached = (time.time() - cache_time < 3600) if 'time' in dir() else False

if generate_btn or (is_cached and cache_key in st.session_state.summary_cache):
    if generate_btn:
        with st.spinner("Generating AI summary with Gemini..."):
            import time as time_module
            summary_result = st.session_state.summarizer.generate_summary(
                complaints,
                selected_dept,
                {'start': datetime.combine(start_date, datetime.min.time()),
                 'end': datetime.combine(end_date, datetime.max.time())}
            )

            # Cache the result
            st.session_state.summary_cache[cache_key] = summary_result
            st.session_state.summary_cache[f"{cache_key}_time"] = time_module.time()
    else:
        summary_result = st.session_state.summary_cache[cache_key]
        st.info("[CACHE] Showing cached summary (generated < 1 hour ago)")

    if not summary_result.get('error'):
        st.success("[SUCCESS] Summary Generated!")

        # Display summary in a nice box
        st.markdown("### Executive Brief")
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1f77b4;">
        {summary_result['summary'].replace(chr(10), '<br>')}
        </div>
        """, unsafe_allow_html=True)

        # Metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.caption(f"Generated: {summary_result['generated_at'][:16]}")
        with col2:
            st.caption(f"Analyzed: {summary_result['complaint_count']} complaints")
        with col3:
            st.caption(f"High Priority: {summary_result['high_priority_count']}")

        # Key issues breakdown
        if summary_result.get('key_issues'):
            st.markdown("#### Top Issues")
            for issue in summary_result['key_issues']:
                st.markdown(f"- **{issue['issue']}**: {issue['count']} complaints ({issue['percentage']}%)")

    else:
        st.error(f"[ERROR] {summary_result.get('error_message', 'Unknown error')}")

st.markdown("---")

# Complaints Table
st.header("[TABLE] Complaint List")

if complaints:
    # Convert to DataFrame for better display
    df = pd.DataFrame(complaints, columns=[
        'ID', 'Type', 'Department', 'Priority', 'Description',
        'Status', 'Created', 'Entities', 'Customer', 'Phone'
    ])

    # Format columns
    df['Created'] = pd.to_datetime(df['Created']).dt.strftime('%Y-%m-%d %H:%M')
    df['Description'] = df['Description'].str[:100] + '...'  # Truncate for display

    # Color code priority
    def highlight_priority(row):
        if row['Priority'] == 'HIGH':
            return ['background-color: #ffcccc'] * len(row)
        elif row['Priority'] == 'MEDIUM':
            return ['background-color: #fff4cc'] * len(row)
        else:
            return [''] * len(row)

    # Display with filters
    st.dataframe(
        df[['ID', 'Type', 'Priority', 'Department', 'Status', 'Customer', 'Created', 'Description']].style.apply(highlight_priority, axis=1),
        use_container_width=True,
        hide_index=True,
        height=400
    )

    # Export functionality
    csv = df.to_csv(index=False)
    st.download_button(
        label="[EXPORT] Export to CSV",
        data=csv,
        file_name=f"complaints_{start_date}_{end_date}.csv",
        mime="text/csv",
        use_container_width=False
    )
else:
    st.info("No complaints found for selected filters.")

# Department Breakdown
st.markdown("---")
st.header("[ANALYTICS] Department & Priority Breakdown")

if complaints:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Complaints by Department")
        dept_counts = {}
        for c in complaints:
            dept = c[2]  # department column
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        # Create bar chart data
        dept_df = pd.DataFrame(list(dept_counts.items()), columns=['Department', 'Count'])
        dept_df = dept_df.sort_values('Count', ascending=False)

        st.bar_chart(dept_df.set_index('Department'))

        # Show metrics
        for dept, count in sorted(dept_counts.items(), key=lambda x: x[1], reverse=True):
            st.metric(dept, count)

    with col2:
        st.subheader("Priority Distribution")
        priority_counts = {}
        for c in complaints:
            priority = c[3]
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        # Show metrics with color coding
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            count = priority_counts.get(priority, 0)
            percentage = (count / len(complaints) * 100) if complaints else 0
            st.metric(
                f"{priority} Priority",
                f"{count} ({percentage:.1f}%)",
                delta="Needs attention" if priority == 'HIGH' and count > 0 else None,
                delta_color="inverse" if priority == 'HIGH' else "off"
            )

        # Pie chart representation
        priority_df = pd.DataFrame(list(priority_counts.items()), columns=['Priority', 'Count'])
        st.bar_chart(priority_df.set_index('Priority'))

else:
    st.info("No data available for analytics.")

# Footer
st.markdown("---")
st.caption("[INFO] Dashboard auto-refreshes on page reload. Summaries are cached for 1 hour to reduce API costs.")
st.caption("[TECH] Powered by TiDB Cloud, Gemini API, and Streamlit")
