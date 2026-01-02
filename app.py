import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# 1. Config & Setup
st.set_page_config(page_title="KACANG KANTOI", page_icon="🥜", layout="wide", initial_sidebar_state="collapsed")
load_dotenv()

# --- THE DESIGN SYSTEM (NYT DARK MODE) ---
st.markdown("""
<style>
    /* IMPORT FONT: Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;900&display=swap');

    /* GLOBAL RESET */
    .stApp {
        background-color: #050505;
        font-family: 'Inter', sans-serif;
    }

    /* REMOVE PADDING */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
    }

    /* --- HERO CARD --- */
    .hero-card {
        background-color: #FFFFFF;
        border: 1px solid #333;
        border-top: 6px solid #FFC107;
        padding: 3rem;
        border-radius: 4px;
        margin-bottom: 3rem;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.6);
    }

    .hero-title {
        font-size: 4rem !important;
        font-weight: 900 !important;
        color: #000000 !important;
        text-transform: uppercase;
        line-height: 0.95;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }

    .hero-subtitle {
        font-size: 1.25rem !important;
        color: #000 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 2rem;
        border-bottom: 4px solid #FFC107;
        display: inline-block;
        padding-bottom: 8px;
    }
    
    .hero-copy {
        color: #1a1a1a;
        font-size: 1.25rem;
        line-height: 1.7; 
        max-width: 900px; 
        font-weight: 500;
    }

    /* TAGS */
    .status-tag {
        background-color: #000;
        color: #FFF;
        padding: 4px 12px;
        font-size: 0.9rem;
        vertical-align: middle;
        font-weight: 700;
        border-radius: 4px;
        margin-left: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .highlight-yellow {
        background-color: #FFC107; 
        padding: 0 6px;
        font-weight: 700;
        color: #000;
    }

    /* --- METRIC DECK --- */
    .metric-container {
        background-color: #111;
        border: 1px solid #222;
        padding: 2rem;
        border-left: 4px solid #444;
        height: 100%;
        transition: all 0.2s;
    }
    
    .metric-container:hover {
        border-left: 4px solid #FFC107;
        background-color: #161616;
        transform: translateY(-2px);
    }

    .metric-label {
        color: #D1D1D1;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
        margin-bottom: 0.75rem;
    }

    .metric-value {
        color: #FFF;
        font-size: 3rem;
        font-weight: 900;
        margin-bottom: 0.25rem;
        letter-spacing: -1px;
        line-height: 1;
    }

    .metric-sub {
        color: #FFC107;
        font-size: 0.95rem;
        font-weight: 600;
        margin-top: 5px;
    }

    /* --- CHART HEADERS --- */
    h3 {
        color: #FFF !important;
        text-transform: uppercase;
        font-weight: 900 !important;
        font-size: 1.8rem !important;
        margin-top: 2rem;
        letter-spacing: 0.5px;
        border-left: 8px solid #FFC107;
        padding-left: 20px;
        margin-bottom: 8px !important;
    }
    
    .chart-caption {
        color: #E0E0E0;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        margin-left: 28px;
        font-weight: 400;
    }

    /* --- DATAFRAME --- */
    [data-testid="stDataFrame"] {
        border: 1px solid #333;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize connection
@st.cache_resource
def init_connection():
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        return None
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

supabase = init_connection()

# Fetch Data
@st.cache_data(ttl=60)
def get_data():
    if not supabase: return pd.DataFrame()
    try:
        response = supabase.table("sentiment_logs").select("*").order("created_at", desc=True).execute()
        df = pd.DataFrame(response.data)
        if not df.empty:
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['date'] = df['created_at'].dt.date
        return df
    except:
        return pd.DataFrame()

df = get_data()

# --- 1. THE HERO STORY ---
st.markdown(f"""
<div class="hero-card">
    <div class="hero-title">KACANG KANTOI <span class="status-tag">INTEL BETA</span></div>
    <div class="hero-subtitle">THE SIGNAL AMIDST THE NOISE.</div>
    <div class="hero-copy">
        Digital conversations are messy. Public sentiment is often invisible.
        <br><br>
        <b>Kacang Kantoi</b> uses autonomous AI agents to audit the <i>gap</i> between official policy and ground reality. 
        We listen to the <span class="highlight-yellow">Malay, English, and Mandarin</span> ecosystems to reveal what 
        traditional polls miss: <b>The raw, unfiltered pulse of the nation.</b>
        <br><br>
        <i>For the curious citizen and the strategic decision-maker.</i>
    </div>
</div>
""", unsafe_allow_html=True)

# Handle Data State
if df.empty:
    st.error("⚠️ SIGNAL LOST. Please initialize the sentiment engine.")
    st.stop()

# Calculate Metrics
total_videos = len(df)
positive_pct = (len(df[df['sentiment'] == 'Positive']) / total_videos * 100)
negative_pct = (len(df[df['sentiment'] == 'Negative']) / total_videos * 100)
top_topic = df['topic'].mode()[0] if not df['topic'].empty else "N/A"

# --- 2. THE INSIGHT DECK ---
c1, c2, c3, c4 = st.columns(4)

def kanto_metric(label, value, sub):
    return f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-sub">{sub}</div>
    </div>
    """

with c1: st.markdown(kanto_metric("DATA POINTS", total_videos, "Conversations Audited"), unsafe_allow_html=True)
with c2: st.markdown(kanto_metric("ALIGNMENT SCORE", f"{positive_pct:.1f}%", "Positive Resonance"), unsafe_allow_html=True)
with c3: st.markdown(kanto_metric("FRICTION INDEX", f"{negative_pct:.1f}%", "Critical Pushback"), unsafe_allow_html=True)
with c4: st.markdown(kanto_metric("PRIMARY VECTOR", top_topic, "High-Impact Theme"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 3. SENTIMENT APPROVAL RATING (NYT STYLE) ---
st.markdown("### PUBLIC SENTIMENT RATING")
st.markdown("<div class='chart-caption'>Daily Approval vs. Disapproval trends. (NYT-Style Analysis)</div>", unsafe_allow_html=True)

if not df.empty:
    # 1. Transform Data: Calculate % of sentiment per day
    daily_counts = df.groupby(['date', 'sentiment']).size().reset_index(name='count')
    daily_totals = df.groupby(['date']).size().reset_index(name='total')
    
    # Merge to get percentages
    daily_trend = pd.merge(daily_counts, daily_totals, on='date')
    daily_trend['percentage'] = (daily_trend['count'] / daily_trend['total']) * 100
    
    # 2. Build the Chart
    fig_trend = go.Figure()

    # Define Color Map
    colors = {'Positive': '#FFC107', 'Negative': '#EF553B', 'Neutral': '#444444'}
    
    for sentiment, color in colors.items():
        subset = daily_trend[daily_trend['sentiment'] == sentiment]
        if not subset.empty:
            # Add Scatter Dots (Raw Polls Look)
            fig_trend.add_trace(go.Scatter(
                x=subset['date'], 
                y=subset['percentage'],
                mode='markers',
                marker=dict(color=color, size=8, opacity=0.4),
                name=f"{sentiment} (Raw)",
                showlegend=False
            ))
            
            # Add Smoothed Line (Trend Look)
            # Simple smooth line connecting points
            fig_trend.add_trace(go.Scatter(
                x=subset['date'], 
                y=subset['percentage'],
                mode='lines',
                line=dict(color=color, width=4, shape='spline', smoothing=1.3),
                name=sentiment
            ))

    # 3. High-Contrast NYT Styling
    fig_trend.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        hovermode="x unified",
        xaxis=dict(
            showgrid=True, 
            gridcolor='#222', 
            tickfont=dict(size=14, color="#DDD"),
            gridwidth=1,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='#222',
            tickfont=dict(size=14, color="#DDD"),
            range=[0, 105], # Lock Y-axis to 0-100%
            ticksuffix="%",
            zeroline=False
        ),
        legend=dict(
            orientation="h", 
            y=1.1, 
            x=0,
            font=dict(size=14, color="#FFF"),
            bgcolor="rgba(0,0,0,0)"
        ),
        margin=dict(t=40, b=40, l=0, r=0)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# --- 4. THE VISUAL NARRATIVE ---
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### ECHO CHAMBER AUDIT")
    st.markdown("<div class='chart-caption'>Are we hearing all voices, or just the loudest ones?</div>", unsafe_allow_html=True)
    if 'persona' in df.columns:
        fig_persona = px.pie(df, names='persona', hole=0.6, 
                            color_discrete_sequence=['#FFC107', '#FFFFFF', '#444444', '#888888'])
        fig_persona.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="white"),
            showlegend=True,
            legend=dict(font=dict(size=14, color="#E0E0E0"), orientation="h", y=-0.1),
            margin=dict(t=30, b=50, l=20, r=20),
            annotations=[dict(text="VOICES", x=0.5, y=0.5, font_size=22, showarrow=False, font_color='#FFFFFF')]
        )
        fig_persona.update_traces(textinfo='percent', textfont_size=16)
        st.plotly_chart(fig_persona, use_container_width=True)

with col2:
    st.markdown("### SENTIMENT HEATMAP")
    st.markdown("<div class='chart-caption'>Identifying where policy meets resistance (Red) or approval (Yellow).</div>", unsafe_allow_html=True)
    if 'topic' in df.columns:
        topic_counts = df.groupby(['topic', 'sentiment']).size().reset_index(name='count')
        fig_topic = px.bar(topic_counts, x='count', y='topic', color='sentiment', orientation='h',
                            color_discrete_map={'Positive': '#FFC107', 'Negative': '#EF553B', 'Neutral': '#888888'})
        
        fig_topic.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="white"),
            xaxis=dict(
                showgrid=True, 
                gridcolor='#333', 
                tickfont=dict(size=14, color="#FFFFFF"),
                title_font=dict(size=16, color="#E0E0E0")
            ), 
            yaxis=dict(
                showgrid=False, 
                tickfont=dict(size=15, color="#FFFFFF", weight="bold")
            ),
            legend=dict(
                font=dict(size=14, color="#E0E0E0"),
                title=dict(font=dict(color="#FFFFFF"))
            ),
            margin=dict(t=30, b=20, l=0, r=0)
        )
        st.plotly_chart(fig_topic, use_container_width=True)

# --- 5. THE EVIDENCE LOG ---
st.markdown("### 🕵️ LIVE INTELLIGENCE FEED")
st.markdown("<div class='chart-caption'>The raw data behind the insights. Filtered for relevance.</div>", unsafe_allow_html=True)

if st.button("🔄 REFRESH INTELLIGENCE"):
    st.cache_data.clear()
    st.rerun()

st.dataframe(
    df[['created_at', 'sentiment', 'persona', 'topic', 'summary', 'raw_comment']],
    use_container_width=True,
    column_config={
        "created_at": st.column_config.DatetimeColumn("TIMESTAMP", format="D MMM, HH:mm"),
        "sentiment": st.column_config.TextColumn("SENTIMENT"),
        "persona": st.column_config.TextColumn("SEGMENT"),
        "topic": st.column_config.TextColumn("THEME"),
        "summary": st.column_config.TextColumn("AI ANALYSIS", width="large"),
        "raw_comment": st.column_config.TextColumn("SOURCE CONTENT", width="medium"),
    },
    hide_index=True
)