import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 1. Config & Setup
st.set_page_config(
    page_title="KACANG KANTOI | War Room", 
    page_icon="🥜", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)
load_dotenv()

# --- THE DESIGN SYSTEM (High-Readability Mode) ---
st.markdown("""
<style>
    /* IMPORT FONT: Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;800;900&display=swap');

    /* GLOBAL RESET */
    .stApp {
        background-color: #050505;
        font-family: 'Inter', sans-serif;
    }

    /* REMOVE PADDING */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
    }

    /* --- HERO CARD --- */
    .hero-card {
        background-color: #FFFFFF;
        border: 1px solid #333;
        border-top: 6px solid #FFC107;
        padding: 3rem;
        border-radius: 2px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.6);
        margin-bottom: 2rem;
    }

    .hero-title {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        color: #000000 !important;
        text-transform: uppercase;
        line-height: 0.95;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }

    .hero-subtitle {
        font-size: 1.2rem !important;
        color: #000 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 1.5rem;
        border-bottom: 4px solid #FFC107;
        display: inline-block;
        padding-bottom: 5px;
    }
    
    /* WAR ROOM BOX */
    .war-room-box {
        background-color: #111;
        border: 1px solid #333;
        border-left: 4px solid #FF5252; /* Red for Alert */
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 30px;
    }
    
    .war-room-header {
        color: #FF5252;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
    
    .war-room-headline {
        color: #FFF;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .war-room-advice {
        color: #CCC;
        font-style: italic;
        font-size: 1rem;
    }

    /* --- METRICS --- */
    [data-testid="stMetricLabel"] {
        color: #888;
        font-size: 0.9rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    [data-testid="stMetricValue"] {
        color: #FFF;
        font-size: 3rem !important;
        font-weight: 800;
    }

    /* --- CHART HEADERS --- */
    h3 {
        color: #FFF !important;
        text-transform: uppercase;
        font-weight: 900 !important;
        font-size: 1.6rem !important;
        letter-spacing: 0.5px;
        border-left: 6px solid #FFC107;
        padding-left: 15px;
        margin-top: 30px !important;
        margin-bottom: 10px !important;
    }
    
    .chart-caption {
        color: #888;
        font-size: 1rem;
        margin-bottom: 20px;
        margin-left: 22px;
    }

    /* --- DATAFRAME --- */
    [data-testid="stDataFrame"] {
        border: 1px solid #222;
        background-color: #0A0A0A;
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

# --- DATA LOADING (UPDATED FOR NEW SCHEMA) ---
def load_data():
    """Fetches valid sentiment logs from the last 24 hours."""
    if not supabase: return pd.DataFrame()
    
    try:
        # Calculate 24h ago timestamp
        yesterday = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        
        # UPDATED: Selects 'topic', 'archetype', 'impact_score', 'specific_trigger'
        response = supabase.table("sentiment_logs") \
            .select("created_at, sentiment, archetype, topic, summary, impact_score, specific_trigger, is_3r") \
            .gte("created_at", yesterday) \
            .order("created_at", desc=True) \
            .execute()
        
        df = pd.DataFrame(response.data)
        
        # Handle empty data
        if df.empty:
            return df
            
        # Type Conversion
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['impact_score'] = pd.to_numeric(df['impact_score'], errors='coerce').fillna(0)
        df['archetype'] = df['archetype'].fillna("Unknown")
        
        return df
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame()

def load_intelligence():
    """Fetches the latest strategic brief from the database."""
    if not supabase: return None
    try:
        response = supabase.table("narrative_briefs") \
            .select("content, net_trust_score, created_at") \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        
        if response.data:
            return response.data[0]
        return None
    except:
        return None

# Load Data
df = load_data()
latest_intel = load_intelligence()

# --- HERO SECTION ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"""
    <div class="hero-card">
        <div class="hero-title">KACANG KANTOI <span style="font-size: 1rem; vertical-align: middle; background: #000; color: #fff; padding: 4px 10px; border-radius: 4px;">LIVE BETA</span></div>
        <div class="hero-subtitle">Political Intelligence Engine</div>
        <div style="color: #333; font-size: 1.1rem; font-weight: 500;">
            Monitoring the <span style="background:#FFC107; padding: 0 4px;">Malay, English, and Mandarin</span> ecosystems using Autonomous AI.
            We quantify the gap between policy intent and public sentiment.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # --- WAR ROOM INTELLIGENCE BOX ---
    if latest_intel:
        content = latest_intel['content']
        alert_color = "#FF5252" if content.get('crisis_alert') else "#4CAF50" # Red vs Green
        alert_text = "CRISIS ALERT" if content.get('crisis_alert') else "STATUS STABLE"
        
        st.markdown(f"""
        <div class="war-room-box" style="border-left: 4px solid {alert_color};">
            <div class="war-room-header" style="color: {alert_color};">🦅 STRATEGIC BRIEFING: {alert_text}</div>
            <div class="war-room-headline">{content.get('headline', 'Analyzing...')}</div>
            <div style="color: #DDD; margin-bottom: 10px; font-size: 0.95rem;">
                <b>Driver:</b> {content.get('key_driver', 'Unknown')}
            </div>
            <div class="war-room-advice">
                "👉 {content.get('actionable_advice', 'No action required.')}"
            </div>
            <div style="margin-top: 10px; font-size: 0.8rem; color: #555;">
                Generated: {pd.to_datetime(latest_intel['created_at']).strftime('%H:%M %p')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Initializing Intelligence Engine...")

# --- METRICS SECTION (THE PUBLIC PULSE) ---
st.markdown("### THE PUBLIC PULSE")
st.markdown("<div class='chart-caption'>Real-time metrics calculated from the last 24 hours of engagement.</div>", unsafe_allow_html=True)

if not df.empty:
    # 1. Net Trust Score (Average Impact Score)
    net_trust = df['impact_score'].mean()
    
    # 2. Resistance (Negative Impact Volume)
    total_impact_vol = df['impact_score'].abs().sum()
    if total_impact_vol > 0:
        resistance_vol = df[df['impact_score'] < 0]['impact_score'].abs().sum()
        resistance_pct = (resistance_vol / total_impact_vol) * 100
    else:
        resistance_pct = 0
    
    # 3. Dominant Topic
    top_topic = df['topic'].mode()[0] if not df['topic'].empty else "None"

    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("Audited Conversations", len(df), delta="Last 24h")
    
    with m2:
        # Color code the score
        score_color = "normal" 
        if net_trust < -0.5: score_color = "inverse" # Red
        
        st.metric(
            "Net Trust Score", 
            f"{net_trust:+.2f}", 
            delta="Political Capital", 
            delta_color=score_color,
            help="Weighted score: Sentiment × Archetype Weight × Risk Multiplier"
        )
        
    with m3:
        st.metric(
            "Resistance Level", 
            f"{resistance_pct:.1f}%", 
            delta="Friction",
            delta_color="off",
            help="Percentage of total political capital being burned by negative sentiment."
        )
        
    with m4:
        st.metric("Dominant Topic", top_topic)

else:
    st.warning("Waiting for data stream... Check scraper status.")


# --- VISUALIZATION ROW 1 ---
col_charts_1, col_charts_2 = st.columns([1, 2])

with col_charts_1:
    st.markdown("### SHARE OF VOICE")
    st.markdown("<div class='chart-caption'>Which archetype is dominating?</div>", unsafe_allow_html=True)
    
    if not df.empty:
        # UPDATED: Use 'archetype' column
        voice_data = df['archetype'].value_counts().reset_index()
        voice_data.columns = ['archetype', 'count']
        
        # Custom Colors for your Archetypes
        color_map = {
            "Heartland Conservative": "#FFA500", # Orange
            "Urban Reformist": "#FFFFFF",        # White
            "Economic Pragmatist": "#808080",    # Grey
            "Digital Cynic": "#FFD700",          # Gold
            "Unknown": "#333333"
        }
        
        fig_donut = px.pie(
            voice_data, 
            values='count', 
            names='archetype', 
            hole=0.6,
            color='archetype',
            color_discrete_map=color_map
        )
        fig_donut.update_layout(
            template="plotly_dark",
            showlegend=True,
            legend=dict(orientation="h", y=-0.1),
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_donut, use_container_width=True)

with col_charts_2:
    st.markdown("### BATTLEFIELD RADAR")
    st.markdown("<div class='chart-caption'>Topic Volume vs. Net Sentiment. Red = Danger Zone.</div>", unsafe_allow_html=True)
    
    if not df.empty:
        # Group by Topic (Updated from 'domain')
        # We calculate count (Volume) and mean impact_score (Sentiment)
        radar_data = df.groupby('topic').agg(
            volume=('topic', 'count'),
            avg_sentiment=('impact_score', 'mean')
        ).reset_index()
        
        fig_radar = px.scatter(
            radar_data,
            x="volume",
            y="avg_sentiment",
            color="avg_sentiment",
            size="volume",
            text="topic",
            color_continuous_scale="RdYlGn", # Red to Green
            range_color=[-2, 2]
        )
        
        fig_radar.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='white')))
        fig_radar.update_layout(
            template="plotly_dark",
            xaxis_title="Engagement Volume",
            yaxis_title="Net Sentiment (Impact)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False
        )
        # Add Reference Lines
        fig_radar.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray")
        
        st.plotly_chart(fig_radar, use_container_width=True)

# --- TRAJECTORY CHART ---
st.markdown("### SENTIMENT TRAJECTORY")
st.markdown("<div class='chart-caption'>Hourly shift in Net Trust Score.</div>", unsafe_allow_html=True)

if not df.empty:
    # Resample to Hourly
    df_trend = df.set_index('created_at').resample('H')['impact_score'].mean().reset_index()
    
    fig_trend = px.line(df_trend, x='created_at', y='impact_score', markers=True)
    fig_trend.update_traces(line_color='#FFC107', line_width=3)
    fig_trend.add_hline(y=0, line_dash="dash", line_color="white", annotation_text="Neutral Baseline")
    
    fig_trend.update_layout(
        template="plotly_dark",
        yaxis_title="Net Trust Score",
        xaxis_title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# --- INTELLIGENCE FEED ---
st.markdown("### LIVE INTELLIGENCE FEED")
st.markdown("<div class='chart-caption'>Raw data filtered for relevance.</div>", unsafe_allow_html=True)

if not df.empty:
    # UPDATED: Columns match the NEW schema
    feed_df = df[['created_at', 'topic', 'specific_trigger', 'archetype', 'impact_score', 'summary']].copy()
    
    st.dataframe(
        feed_df,
        use_container_width=True,
        column_config={
            "created_at": st.column_config.DatetimeColumn("Timestamp", format="D MMM, HH:mm"),
            "topic": "Domain",
            "specific_trigger": "Trigger",
            "archetype": "Persona",
            "impact_score": st.column_config.NumberColumn("Score", format="%.2f"),
            "summary": "AI Analysis"
        },
        hide_index=True
    )

# --- METHODOLOGY FOOTER ---
with st.expander("METHODOLOGY: THE 'KACANG KANTOI' ALGORITHM"):
    st.markdown("""
    #### 1. The Harvest (Real-Time)
    Every 60 minutes, we scrape TikTok for trilingual keywords (Malay, English, Mandarin) related to Malaysian politics. We sort by **Recency** to capture breaking news.
    
    #### 2. The Intelligence (Gemini 2.0 Flash)
    We use a fine-tuned prompt to classify content into 4 Archetypes and detect "3R" (Race, Religion, Royalty) risks.
    
    #### 3. The Net Trust Score (NTS)
    We don't just count likes. We calculate **Political Impact**:
    $$ NTS = Sentiment \\times Archetype Weight \\times Risk Multiplier $$
    
    * **Heartland Conservative (2.5x):** High electoral impact.
    * **Economic Pragmatist (1.5x):** Swing voter impact.
    * **Urban Reformist (1.0x):** Base voter impact.
    * **Digital Cynic (0.5x):** Low impact (noise).
    * **3R Risk:** If a topic touches 3R, it gets a **1.5x multiplier** on negative sentiment.
    """)