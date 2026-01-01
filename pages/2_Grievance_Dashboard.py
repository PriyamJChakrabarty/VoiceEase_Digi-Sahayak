"""
Grievance Dashboard - Customer Complaints & Issues
Track and manage customer problems and complaints
"""

import streamlit as st
from datetime import datetime, timedelta
from conversation_manager import ConversationManager
from complaint_summarizer import ComplaintSummarizer
from db import engine
import pandas as pd
import os
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

load_dotenv()

st.set_page_config(
    page_title="Grievance Dashboard",
    page_icon="⚠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with proper text contrast
st.markdown("""
<style>
    /* Main background - Clean professional light */
    .stApp {
        background: #f8f9fa;
    }

    /* Sidebar styling - Dark background with LIGHT text */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Main content area - white card effect with DARK text */
    .main .block-container {
        background: white;
        border-radius: 20px;
        padding: 2rem 3rem;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        margin: 2rem auto;
    }

    /* Headers - DARK text on light background */
    h1 {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        color: #2d3748 !important;
        font-weight: 700;
        font-size: 1.8rem !important;
        margin-top: 2rem !important;
    }

    h3 {
        color: #4a5568 !important;
        font-weight: 600;
    }

    /* Metric cards with good contrast */
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: #ffffff;  /* LIGHT text on dark gradient */
        box-shadow: 0 8px 20px rgba(245, 87, 108, 0.4);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(245, 87, 108, 0.6);
    }

    .metric-card-orange {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        box-shadow: 0 8px 20px rgba(250, 112, 154, 0.4);
    }

    .metric-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        box-shadow: 0 8px 20px rgba(17, 153, 142, 0.4);
    }

    .metric-card-blue {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
        color: #ffffff;  /* LIGHT text */
    }

    .metric-label {
        font-size: 0.9rem;
        opacity: 0.95;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #ffffff;  /* LIGHT text */
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: #ffffff !important;  /* LIGHT text */
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(245, 87, 108, 0.4);
    }

    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: #ffffff !important;
    }

    /* Modern Table Styling */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }

    .dataframe thead tr th {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        color: #ffffff !important;  /* LIGHT text on dark background */
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        padding: 1rem 0.75rem !important;
        font-size: 0.85rem !important;
    }

    .dataframe tbody tr {
        border-bottom: 1px solid #e2e8f0 !important;
        transition: all 0.2s ease !important;
    }

    .dataframe tbody tr:hover {
        background: #f7fafc !important;
        transform: scale(1.005);
    }

    .dataframe tbody tr td {
        padding: 0.9rem 0.75rem !important;
        font-size: 0.9rem !important;
        color: #2d3748 !important;  /* DARK text on light background */
    }

    /* Summary box */
    .summary-box {
        background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
        border-radius: 15px;
        padding: 2rem;
        border-left: 6px solid #f5576c;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
    }

    .summary-box h3 {
        color: #f5576c !important;
    }

    .summary-box p {
        color: #2d3748 !important;  /* DARK text on light background */
    }

    /* Info boxes with proper contrast */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }

    /* Dark text on light info boxes */
    .stAlert p, .stAlert div {
        color: #2d3748 !important;
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        color: #a0aec0 !important;  /* Medium gray for readability */
        font-size: 0.85rem;
        border-top: 1px solid #e2e8f0;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

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

# Header
st.markdown("<h1>⚠️ Grievance Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #718096; font-size: 1.1rem; margin-bottom: 2rem;'>Real-time tracking and AI-powered analytics for customer complaints</p>", unsafe_allow_html=True)

# Filters Section - Sidebar
st.sidebar.markdown("## 🔍 Filters")
st.sidebar.markdown("---")

departments = [
    "All Departments",
    "Network Operations",
    "Billing Department",
    "Technical Support",
    "Customer Support"
]

dept_icons = {
    "All Departments": "🌐",
    "Network Operations": "📡",
    "Billing Department": "💰",
    "Technical Support": "🔧",
    "Customer Support": "👥"
}

selected_dept = st.sidebar.selectbox(
    "Department",
    departments,
    format_func=lambda x: f"{dept_icons.get(x, '')} {x}"
)

st.sidebar.markdown("### 📅 Date Range")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("From", datetime.now() - timedelta(days=30))
with col2:
    end_date = st.date_input("To", datetime.now())

st.sidebar.markdown("### 📌 Status Filter")
status_filter = st.sidebar.selectbox(
    "Status",
    ["all", "open", "in_progress", "resolved", "closed"],
    format_func=lambda x: {
        "all": "🔵 All Status",
        "open": "🔴 Open",
        "in_progress": "🟡 In Progress",
        "resolved": "🟢 Resolved",
        "closed": "⚫ Closed"
    }.get(x, x)
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip**: Grievances are customer complaints requiring resolution action.")

# Fetch grievances
dept_filter = None if selected_dept == "All Departments" else selected_dept
status = None if status_filter == "all" else status_filter

try:
    grievances = st.session_state.conv_manager.get_grievances(
        department=dept_filter,
        start_date=datetime.combine(start_date, datetime.min.time()),
        end_date=datetime.combine(end_date, datetime.max.time()),
        status=status
    )
except Exception as e:
    st.error(f"❌ Error fetching grievances: {e}")
    grievances = []

# Key Metrics Section
st.markdown("## 📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Grievances</div>
        <div class="metric-value">{len(grievances)}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    open_count = sum(1 for g in grievances if g[4] == 'open')
    st.markdown(f"""
    <div class="metric-card metric-card-orange">
        <div class="metric-label">Open Cases</div>
        <div class="metric-value">{open_count}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    in_progress = sum(1 for g in grievances if g[4] == 'in_progress')
    st.markdown(f"""
    <div class="metric-card metric-card-blue">
        <div class="metric-label">In Progress</div>
        <div class="metric-value">{in_progress}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    resolved = sum(1 for g in grievances if g[4] == 'resolved')
    resolution_rate = (resolved / len(grievances) * 100) if grievances else 0
    st.markdown(f"""
    <div class="metric-card metric-card-green">
        <div class="metric-label">Resolution Rate</div>
        <div class="metric-value">{resolution_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# AI Summary Section
st.markdown("## 🤖 AI Executive Summary")
st.markdown("<p style='color: #718096;'>Generate intelligent insights from grievance data using Google Gemini AI</p>", unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])
with col1:
    st.info("📝 Our AI analyzes patterns, sentiment, and trends to provide actionable insights")
with col2:
    generate_btn = st.button("✨ Generate Summary", type="primary", use_container_width=True)

# Check cache
cache_key = f"{selected_dept}_{start_date}_{end_date}_{len(grievances)}"

if generate_btn:
    with st.spinner("🔄 Analyzing grievances with Gemini AI..."):
        import time as time_module
        summary_result = st.session_state.summarizer.generate_summary(
            grievances,
            selected_dept,
            {'start': datetime.combine(start_date, datetime.min.time()),
             'end': datetime.combine(end_date, datetime.max.time())}
        )

        # Cache the result
        st.session_state.summary_cache[cache_key] = summary_result
        st.session_state.summary_cache[f"{cache_key}_time"] = time_module.time()

if cache_key in st.session_state.summary_cache:
    summary_result = st.session_state.summary_cache.get(cache_key)

    if summary_result and not summary_result.get('error'):
        st.success("✅ Summary Generated Successfully!")

        # Display summary
        st.markdown(f"""
        <div class="summary-box">
            <h3>📄 Executive Brief</h3>
            <p style="font-size: 1.05rem; line-height: 1.8;">
            {summary_result['summary'].replace(chr(10), '<br><br>')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Metadata
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"🕒 **Generated:** {summary_result['generated_at'][:16]}")
        with col2:
            st.markdown(f"📊 **Analyzed:** {summary_result['complaint_count']} grievances")

st.markdown("---")

# Grievances Table Section
st.markdown("## 📋 Grievance Details")

if grievances:
    # Convert to DataFrame
    df = pd.DataFrame(grievances, columns=[
        'ID', 'Type', 'Department', 'Description',
        'Status', 'Created', 'Entities', 'Customer', 'Phone'
    ])

    # Format columns
    df['Created'] = pd.to_datetime(df['Created']).dt.strftime('%Y-%m-%d %H:%M')

    # Create display dataframe
    display_df = df[['ID', 'Type', 'Department', 'Status', 'Customer', 'Created']].copy()

    # Modern styling function with status-based colors
    def style_table(row):
        status_colors = {
            'open': ('4px solid #f5576c', '#fff5f7', '#f5576c'),
            'in_progress': ('4px solid #a29bfe', '#f5f3ff', '#a29bfe'),
            'resolved': ('4px solid #00b894', '#f0fff4', '#00b894'),
            'closed': ('4px solid #636e72', '#f7fafc', '#636e72')
        }

        status = row['Status']
        border, bg, text_color = status_colors.get(status, ('4px solid #667eea', '#f8f9fa', '#667eea'))

        return [
            f'border-left: {border}; background-color: {bg}; font-weight: 500;',
            f'background-color: {bg};',
            f'background-color: {bg};',
            f'background-color: {bg}; color: {text_color}; font-weight: 700;',
            f'background-color: {bg};',
            f'background-color: {bg}; color: #718096; font-size: 0.85rem;'
        ]

    st.dataframe(
        display_df.style.apply(style_table, axis=1),
        use_container_width=True,
        hide_index=True,
        height=450
    )

    # Export functionality
    csv = df.to_csv(index=False)
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"grievances_{start_date}_{end_date}.csv",
            mime="text/csv",
            use_container_width=True
        )
else:
    st.info("🔍 No grievances found for the selected filters. Try adjusting your search criteria.")

st.markdown("---")

# Analytics Section
st.markdown("## 📊 Analytics & Insights")

if grievances:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🏢 Department Distribution")

        # Department breakdown
        dept_counts = {}
        for g in grievances:
            dept = g[2]
            dept_counts[dept] = dept_counts.get(dept, 0) + 1

        dept_df = pd.DataFrame(list(dept_counts.items()), columns=['Department', 'Count'])
        dept_df = dept_df.sort_values('Count', ascending=False)

        # Create bar chart
        fig_dept = px.bar(
            dept_df,
            x='Count',
            y='Department',
            orientation='h',
            color='Count',
            color_continuous_scale='Reds',
            text='Count'
        )

        fig_dept.update_layout(
            showlegend=False,
            height=350,
            margin=dict(l=0, r=0, t=30, b=0),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='#2d3748')
        )

        fig_dept.update_traces(textposition='outside')
        st.plotly_chart(fig_dept, use_container_width=True)

    with col2:
        st.markdown("### 🎯 Status Breakdown")

        # Status distribution
        status_counts = {}
        for g in grievances:
            status = g[4]
            status_counts[status] = status_counts.get(status, 0) + 1

        status_df = pd.DataFrame(list(status_counts.items()), columns=['Status', 'Count'])

        # Create donut chart
        colors = {
            'open': '#f5576c',
            'in_progress': '#a29bfe',
            'resolved': '#00b894',
            'closed': '#636e72'
        }
        fig_status = go.Figure(data=[go.Pie(
            labels=status_df['Status'],
            values=status_df['Count'],
            hole=0.5,
            marker_colors=[colors.get(s, '#667eea') for s in status_df['Status']],
            textinfo='label+percent',
            textfont_size=14
        )])

        fig_status.update_layout(
            showlegend=True,
            height=350,
            margin=dict(l=0, r=0, t=30, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='#2d3748')
        )

        st.plotly_chart(fig_status, use_container_width=True)

else:
    st.info("📊 No data available for analytics. Apply different filters to see insights.")

# Footer
st.markdown("""
<div class="footer">
    <p><strong>🔄 Auto-refresh:</strong> Dashboard updates on page reload | <strong>💾 Cache:</strong> AI summaries cached for efficiency</p>
    <p><strong>⚡ Powered by:</strong> TiDB Cloud • Google Gemini AI • Streamlit • Plotly</p>
</div>
""", unsafe_allow_html=True)
