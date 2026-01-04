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

# --- THE DESIGN SYSTEM (Restored Manifesto Style) ---
st.markdown("""
<style>
    /* IMPORT FONT: Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

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

    /* --- HERO CARD (The "Manifesto" Look) --- */
    .hero-card {
        background-color: #FFFFFF;
        border: 1px solid #333;
        border-top: 6px solid #FFC107; /* Brand Yellow */
        padding: 3.5rem;
        border-radius: 2px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.8);
        margin-bottom: 3rem;
    }

    .hero-title {
        font-size: 4rem !important;
        font-weight: 900 !important;
        color: #000000 !important;
        text-transform: uppercase;
        line-height: 0.9;
        letter-spacing: -2px;
        margin-bottom: 10px;
    }

    .hero-subtitle {
        font-size: 1.4rem !important;
        color: #000 !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 1.5rem;
        border-bottom: 4px solid #FFC107;
        display: inline-block;
        padding-bottom: 5px;
    }
    
    .hero-copy {
        font-size: 1.15rem;
        color: #333;
        font-weight: 500;
        line-height: 1.6;
        max-width: 800px;
    }

    /* --- METRICS (High Readability) --- */
    [data-testid="stMetricLabel"] {
        color: #888;
        font-size: 0.95rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 700;
    }
    
    [data-testid="stMetricValue"] {
        color: #FFF;
        font-size: 3.8rem !important; /* Bigger for impact */
        font-weight: 800;
        line-height: 1.1;
    }
    
    [data-testid="stMetricDelta"] {
        font-weight: 600;
        background-color: #111;
        padding: 4px 8px;
        border-radius: 4px;
    }

    /* --- NARRATIVE CONTEXT BOX (The "Why") --- */
    .narrative-box {
        background-color: #111;
        border-left: 4px solid #FFC107;
        padding: 20px 25px;
        margin-top: 0px;
        margin-bottom: 40px;
        border-radius: 0 4px 4px 0;
    }
    
    .narrative-header {
        color: #FFC107;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.9rem;
        margin-bottom: 8px;
        letter-spacing: 1px;
    }
    
    .narrative-text {
        color: #E0E0E0;
        font-size: 1.15rem;
        line-height: 1.6;
        font-weight: 400;
    }

    /* --- CHART HEADERS --- */
    h3 {
        color: #FFF !important;
        text-transform: uppercase;
        font-weight: 900 !important;
        font-size: 1.8rem !important;
        letter-spacing: -0.5px;
        border-left: 8px solid #FFC107;
        padding-left: 20px;
        margin-top: 40px !important;
        margin-bottom: 5px !important;
    }
    
    .chart-caption {
        color: #999;
        font-size: 1.05rem;
        margin-bottom: 25px;
        margin-left: 30px;
        font-weight: 400;
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

# --- DATA LOADING ---
def load_data():
    """Fetches valid sentiment logs from the last 24 hours."""
    if not supabase: return pd.DataFrame()
    
    try:
        # Calculate 24h ago timestamp
        yesterday = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        
        # Selects 'topic', 'archetype', 'impact_score', 'specific_trigger'
        response = supabase.table("sentiment_logs") \
            .select("created_at, sentiment, archetype, topic, summary, impact_score, specific_trigger, is_3r") \
            .gte("created_at", yesterday) \
            .order("created_at", desc=True) \
            .execute()
        
        df = pd.DataFrame(response.data)
        
        if df.empty: return df
            
        # Type Conversion
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['impact_score'] = pd.to_numeric(df['impact_score'], errors='coerce').fillna(0)
        df['archetype'] = df['archetype'].fillna("Unknown")
        
        return df
    except Exception as e:
        st.error(f"Data Load Error: {e}")
        return pd.DataFrame()

def load_intelligence():
    """Fetches the latest strategic brief."""
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

# --- HERO SECTION (RESTORED) ---
st.markdown(f"""
<div class="hero-card">
    <div class="hero-title">KACANG KANTOI <span style="font-size: 1.1rem; vertical-align: middle; background: #000; color: #fff; padding: 6px 12px; border-radius: 4px; letter-spacing: 1px;">INTEL BETA</span></div>
    <div class="hero-subtitle">The Signal Amidst The Noise.</div>
    <div class="hero-copy">
        Digital conversations are noisy. Public sentiment is often invisible.
        <br><br>
        <b>Kacang Kantoi</b> deploys <i>autonomous intelligence</i> to audit the gap between official policy and ground reality. 
        We scan the <span style="background:#FFC107; padding: 0 4px; font-weight:700;">Malay, English, and Mandarin</span> ecosystems to reveal what 
        traditional polls miss: <b>The unfiltered pulse of the nation.</b>
    </div>
</div>
""", unsafe_allow_html=True)

# --- METRICS SECTION ---
st.markdown("### THE PUBLIC PULSE")
st.markdown("<div class='chart-caption'>Real-time metrics calculated from the last 24 hours of engagement.</div>", unsafe_allow_html=True)

if not df.empty:
    # Calculations
    net_trust = df['impact_score'].mean()
    
    total_impact_vol = df['impact_score'].abs().sum()
    if total_impact_vol > 0:
        resistance_vol = df[df['impact_score'] < 0]['impact_score'].abs().sum()
        resistance_pct = (resistance_vol / total_impact_vol) * 100
        consensus_pct = 100 - resistance_pct
    else:
        resistance_pct = 0
        consensus_pct = 0
    
    # 3. Dominant Topic
    top_topic = df['topic'].mode()[0] if not df['topic'].empty else "None"

    # METRICS ROW
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric("Audited Conversations", len(df), delta="Last 24h")
    
    with m2:
        st.metric("Public Consensus", f"{consensus_pct:.1f}%", delta="Approval")
        
    with m3:
        st.metric(
            "Resistance Level", 
            f"{resistance_pct:.1f}%", 
            delta="Friction",
            delta_color="off" # Grey delta
        )
        
    with m4:
        # Display the Headline Topic Here
        st.metric("Dominant Topic", top_topic)

    # --- NARRATIVE CONTEXT (THE "WHY") ---
    # This sits immediately below the metrics to explain the "Dominant Topic"
    if latest_intel:
        content = latest_intel['content']
        narrative_text = content.get('dominant_narrative', 'Analyzing narrative patterns...')
        
        st.markdown(f"""
        <div class="narrative-box">
            <div class="narrative-header">🦅 AI Analyst Context</div>
            <div class="narrative-text">"{narrative_text}"</div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.warning("Waiting for data stream... Check scraper status.")


# --- VISUALIZATION ROW ---
col_charts_1, col_charts_2 = st.columns([1, 2])

with col_charts_1:
    st.markdown("### SHARE OF VOICE")
    st.markdown("<div class='chart-caption'>Which persona is dominating the microphone?</div>", unsafe_allow_html=True)
    
    if not df.empty:
        voice_data = df['archetype'].value_counts().reset_index()
        voice_data.columns = ['archetype', 'count']
        
        # Brand Colors
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
            legend=dict(orientation="h", y=-0.15, font=dict(size=12)),
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig_donut.update_traces(textinfo='percent', textfont_size=14)
        st.plotly_chart(fig_donut, use_container_width=True)

with col_charts_2:
    st.markdown("### THE FRICTION RADAR")
    st.markdown("<div class='chart-caption'>Where policy meets resistance (Red) or approval (Green).</div>", unsafe_allow_html=True)
    
    if not df.empty:
        # Group by Topic for Radar
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
            range_color=[-2, 2],
            size_max=60
        )
        
        fig_radar.update_traces(textposition='top center', textfont=dict(size=14, color="white"))
        fig_radar.update_layout(
            template="plotly_dark",
            xaxis_title="Engagement Volume",
            yaxis_title="Net Sentiment (Impact)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            margin=dict(t=20, b=20, l=0, r=0)
        )
        # Baseline
        fig_radar.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray")
        
        st.plotly_chart(fig_radar, use_container_width=True)

# --- TRAJECTORY CHART ---
st.markdown("### THE TRAJECTORY OF TRUST")
st.markdown("<div class='chart-caption'>Tracking how public sentiment shifts hour-by-hour.</div>", unsafe_allow_html=True)

if not df.empty:
    # Resample to Hourly
    df_trend = df.set_index('created_at').resample('H')['impact_score'].mean().reset_index()
    
    fig_trend = px.line(df_trend, x='created_at', y='impact_score', markers=True)
    fig_trend.update_traces(line_color='#FFC107', line_width=4, marker=dict(size=8, color='#FFF'))
    fig_trend.add_hline(y=0, line_dash="dash", line_color="white", annotation_text="Neutral Baseline")
    
    fig_trend.update_layout(
        template="plotly_dark",
        yaxis_title="Net Trust Score",
        xaxis_title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode="x unified"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# --- INTELLIGENCE FEED ---
st.markdown("### LIVE INTELLIGENCE FEED")
st.markdown("<div class='chart-caption'>Raw data filtered for relevance.</div>", unsafe_allow_html=True)

if not df.empty:
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

# --- FOOTER ---
with st.expander("METHODOLOGY: HOW WE LISTEN"):
    st.markdown("""
    #### 1. THE HARVEST
    Every 60 minutes, our autonomous system scans the ecosystem for high-velocity discussions. We filter for relevance, ensuring we capture the *average* voice, not just influencers.
    
    #### 2. THE INTELLIGENCE (Gemini 2.0 Pro)
    We employ Google's Gemini 2.0 Pro engine, tuned to understand Malaysian context (*Manglish, Bahasa Rojak*). It categorizes content into 5 Mutually Exclusive Domains (e.g., Economic Anxiety, Institutional Integrity).
    
    #### 3. THE METRICS
    * **Public Consensus:** The ratio of Positive to Total voices.
    * **Resistance Level:** The ratio of Negative to Total voices.
    * **Dominant Narrative:** AI-generated summary of the highest velocity topic.
    """)