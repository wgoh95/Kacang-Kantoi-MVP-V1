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
        padding: 4rem;
        border-radius: 2px;
        box-shadow: 0px 10px 40px rgba(0,0,0,0.6);
    }

    .hero-title {
        font-size: 4.2rem !important;
        font-weight: 900 !important;
        color: #000000 !important;
        text-transform: uppercase;
        line-height: 0.95;
        margin-bottom: 0.8rem;
        letter-spacing: -2px;
    }

    .hero-subtitle {
        font-size: 1.4rem !important;
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
        font-size: 1.4rem;
        line-height: 1.6; 
        max-width: 950px; 
        font-weight: 500;
        margin-top: 1rem;
    }

    /* TAGS */
    .status-tag {
        background-color: #000;
        color: #FFF;
        padding: 6px 14px;
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

    /* --- METRICS (Typography Optimization) --- */
    [data-testid="stMetricLabel"] {
        color: #999;
        font-size: 1rem !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    
    [data-testid="stMetricValue"] {
        color: #FFF;
        font-size: 3.5rem !important; /* Larger for impact */
        font-weight: 800;
        line-height: 1.2;
    }

    [data-testid="stMetricDelta"] {
        font-weight: 600;
        font-size: 1rem !important;
    }
    
    /* Custom Context Box for Primary Vector */
    .context-box {
        font-size: 0.95rem;
        color: #BBB;
        border-left: 2px solid #FFC107;
        padding-left: 10px;
        margin-top: -10px;
        line-height: 1.4;
        font-style: italic;
    }

    /* --- CHART HEADERS --- */
    h3 {
        color: #FFF !important;
        text-transform: uppercase;
        font-weight: 900 !important;
        font-size: 1.8rem !important;
        letter-spacing: 0.5px;
        border-left: 6px solid #FFC107;
        padding-left: 20px;
        margin-bottom: 12px !important;
    }
    
    .chart-caption {
        color: #BBB;
        font-size: 1.15rem;
        margin-bottom: 2.5rem;
        margin-left: 26px;
        font-weight: 400;
        opacity: 0.9;
        max-width: 700px;
        line-height: 1.5;
    }

    /* --- DATAFRAME --- */
    [data-testid="stDataFrame"] {
        border: 1px solid #333;
        background-color: #0A0A0A;
        font-size: 1.05rem; /* Better readability */
    }
    
    /* --- FOOTER TYPOGRAPHY --- */
    .methodology-text {
        font-size: 1.2rem !important;
        line-height: 1.8 !important;
        color: #DDD !important;
    }
    
    .methodology-header {
        font-size: 1.4rem !important;
        font-weight: 800 !important;
        color: #FFC107 !important;
        margin-bottom: 1rem !important;
        display: block;
        text-transform: uppercase;
        margin-top: 1.5rem;
    }
    
    .methodology-sub {
        font-weight: 700;
        color: #FFF;
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
        # Fetching all records sorted by time
        response = supabase.table("sentiment_logs").select("*").order("created_at", desc=True).execute()
        df = pd.DataFrame(response.data)
        if not df.empty:
            # Ensure proper datetime conversion with UTC
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['date'] = df['created_at'].dt.date
        return df
    except:
        return pd.DataFrame()

df = get_data()

# --- HELPER: SPACER ---
def add_spacer():
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

# --- 1. THE HERO STORY ---
st.markdown(f"""
<div class="hero-card">
    <div class="hero-title">KACANG KANTOI <span class="status-tag">INTEL BETA</span></div>
    <div class="hero-subtitle">THE SIGNAL AMIDST THE NOISE.</div>
    <div class="hero-copy">
        Digital conversations are noisy. Public sentiment is often invisible.
        <br><br>
        <b>Kacang Kantoi</b> deploys <i>autonomous intelligence</i> to audit the gap between official policy and ground reality. 
        We scan the <span class="highlight-yellow">Malay, English, and Mandarin</span> ecosystems to reveal what 
        traditional polls miss: <b>The unfiltered pulse of the nation.</b>
    </div>
</div>
""", unsafe_allow_html=True)

add_spacer()

# Handle Data State
if df.empty:
    st.error("SIGNAL LOST. Please initialize the sentiment engine.")
    st.stop()

# --- METRIC CALCULATIONS (SMART DELTA WITH TIMEZONE FIX) ---
# 1. Total Count
total_videos = len(df)

# 2. Time Splitting (FIXED: Using pd.Timestamp.now(tz='UTC'))
# This ensures we are comparing UTC database time with UTC system time.
now_utc = pd.Timestamp.now(tz='UTC')

current_window = df[df['created_at'] > (now_utc - pd.Timedelta(hours=24))]
previous_window = df[(df['created_at'] <= (now_utc - pd.Timedelta(hours=24))) & 
                     (df['created_at'] > (now_utc - pd.Timedelta(hours=48)))]

# 3. Consensus Logic
if not current_window.empty:
    curr_pos_count = len(current_window[current_window['sentiment'] == 'Positive'])
    curr_total = len(current_window)
    curr_pos_pct = (curr_pos_count / curr_total) * 100
else:
    # Fallback if no recent data (use global)
    curr_pos_pct = (len(df[df['sentiment'] == 'Positive']) / total_videos * 100)

# 4. Resistance Logic
if not current_window.empty:
    curr_neg_count = len(current_window[current_window['sentiment'] == 'Negative'])
    curr_total = len(current_window) # Re-calculate total to be safe
    curr_neg_pct = (curr_neg_count / curr_total) * 100
else:
    curr_neg_pct = (len(df[df['sentiment'] == 'Negative']) / total_videos * 100)

# 5. Trend Calculation
delta_consensus = "Establishing Baseline"
delta_color_consensus = "off" # Gray

delta_resistance = "Establishing Baseline"
delta_color_resistance = "off"

if not previous_window.empty:
    # Calc Previous Pct
    prev_total = len(previous_window)
    if prev_total > 0:
        prev_pos_pct = (len(previous_window[previous_window['sentiment'] == 'Positive']) / prev_total) * 100
        prev_neg_pct = (len(previous_window[previous_window['sentiment'] == 'Negative']) / prev_total) * 100
        
        # Consensus Trend
        diff_pos = curr_pos_pct - prev_pos_pct
        if abs(diff_pos) < 1.0:
            delta_consensus = "Stable (Neutral)"
            delta_color_consensus = "off"
        else:
            delta_consensus = f"{diff_pos:+.1f}% vs 24h ago"
            delta_color_consensus = "normal" # Green if up, Red if down

        # Resistance Trend (Inverse: Down is Good)
        diff_neg = curr_neg_pct - prev_neg_pct
        if abs(diff_neg) < 1.0:
            delta_resistance = "Stable (Neutral)"
            delta_color_resistance = "off"
        else:
            delta_resistance = f"{diff_neg:+.1f}% vs 24h ago"
            delta_color_resistance = "inverse" # Red if up, Green if down

# 6. Dominant Conversation & Dynamic Context
if not df['topic'].empty:
    top_topic = df['topic'].mode()[0]
    # Get the latest summary for this specific topic to provide context
    try:
        latest_topic_row = df[df['topic'] == top_topic].iloc[0]
        context_text = f"Latest trigger: \"{latest_topic_row['summary']}\""
    except:
        context_text = "Emerging pattern detected."
else:
    top_topic = "N/A"
    context_text = "No data available."

# --- 2. THE PUBLIC PULSE (METRICS) ---
st.markdown("### THE PUBLIC PULSE")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Conversations Audited",
        value=total_videos,
        help="Total volume of unique data points ingested."
    )

with col2:
    st.metric(
        label="Public Consensus",
        value=f"{curr_pos_pct:.1f}%",
        delta=delta_consensus,
        delta_color=delta_color_consensus,
        help="The percentage of voices that actively support the narrative. 'Stable' indicates no significant shift from previous baseline."
    )

with col3:
    st.metric(
        label="Resistance Level",
        value=f"{curr_neg_pct:.1f}%",
        delta=delta_resistance,
        delta_color=delta_color_resistance,
        help="The intensity of disagreement. A score >50% indicates significant friction."
    )

with col4:
    st.metric(
        label="Dominant Conversation",
        value=top_topic,
        help="The primary vector driving engagement based on keyword velocity."
    )
    # Dynamic Context Box
    st.markdown(f"<div class='context-box'>{context_text}</div>", unsafe_allow_html=True)

add_spacer()

# --- 3. TRAJECTORY OF TRUST (TRENDS) ---
st.markdown("### THE TRAJECTORY OF TRUST")
st.markdown("<div class='chart-caption'>Tracking how public sentiment shifts hour-by-hour in response to real-world events.</div>", unsafe_allow_html=True)

if not df.empty:
    # 1. Transform Data
    daily_counts = df.groupby(['date', 'sentiment']).size().reset_index(name='count')
    daily_totals = df.groupby(['date']).size().reset_index(name='total')
    daily_trend = pd.merge(daily_counts, daily_totals, on='date')
    daily_trend['percentage'] = (daily_trend['count'] / daily_trend['total']) * 100
    
    # 2. Build Chart
    fig_trend = go.Figure()
    colors = {'Positive': '#FFC107', 'Negative': '#EF553B', 'Neutral': '#444444'}
    
    for sentiment, color in colors.items():
        subset = daily_trend[daily_trend['sentiment'] == sentiment]
        if not subset.empty:
            # Scatter Dots
            fig_trend.add_trace(go.Scatter(
                x=subset['date'], 
                y=subset['percentage'],
                mode='markers',
                marker=dict(color=color, size=8, opacity=0.4),
                name=f"{sentiment} (Raw)",
                showlegend=False
            ))
            # Smooth Line
            fig_trend.add_trace(go.Scatter(
                x=subset['date'], 
                y=subset['percentage'],
                mode='lines',
                line=dict(color=color, width=4, shape='spline', smoothing=1.3),
                name=sentiment
            ))

    # 3. Styling
    fig_trend.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        hovermode="x unified",
        xaxis=dict(showgrid=True, gridcolor='#222', tickfont=dict(size=14, color="#DDD"), zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#222', tickfont=dict(size=14, color="#DDD"), range=[0, 105], ticksuffix="%", zeroline=False),
        legend=dict(orientation="h", y=1.1, x=0, font=dict(size=14, color="#FFF"), bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=40, b=40, l=0, r=0)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

add_spacer()

# --- 4. VISUAL NARRATIVE (PIE & HEATMAP) ---
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### SHARE OF VOICE")
    st.markdown("<div class='chart-caption'>Which persona is dominating the microphone?</div>", unsafe_allow_html=True)
    
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
        
        st.info("💡 **Intel:** A high 'Digital Cynic' share suggests the narrative has been hijacked by satire. Traditional messaging will likely fail here.")

with col2:
    st.markdown("### TOPIC TOXICITY SCANNER")
    st.markdown("<div class='chart-caption'>Where policy meets resistance (Red) or approval (Yellow).</div>", unsafe_allow_html=True)
    
    if 'topic' in df.columns:
        topic_counts = df.groupby(['topic', 'sentiment']).size().reset_index(name='count')
        fig_topic = px.bar(topic_counts, x='count', y='topic', color='sentiment', orientation='h',
                            color_discrete_map={'Positive': '#FFC107', 'Negative': '#EF553B', 'Neutral': '#888888'})
        
        fig_topic.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)", 
            font=dict(color="white"),
            xaxis=dict(showgrid=True, gridcolor='#333', tickfont=dict(size=14, color="#FFFFFF"), title="Volume of Engagement"), 
            yaxis=dict(showgrid=False, tickfont=dict(size=15, color="#FFFFFF", weight="bold"), title=None),
            legend=dict(font=dict(size=14, color="#E0E0E0"), title=None),
            margin=dict(t=30, b=20, l=0, r=0)
        )
        st.plotly_chart(fig_topic, use_container_width=True)

add_spacer()

# --- 5. THE EVIDENCE LOG ---
st.markdown("### LIVE INTELLIGENCE FEED")
st.markdown("<div class='chart-caption'>The raw data behind the insights. Filtered for relevance.</div>", unsafe_allow_html=True)

if st.button("REFRESH INTELLIGENCE"):
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

add_spacer()

# --- 6. FOOTER: METHODOLOGY ---
with st.expander("METHODOLOGY: HOW WE LISTEN"):
    st.markdown("""
    <div class="methodology-text">
        <span class="methodology-header">1. THE HARVEST</span>
        Every 60 minutes, our autonomous system scans the ecosystem for high-velocity discussions surrounding Malaysian public policy. 
        We filter for relevance, ensuring we capture the <i>average</i> voice, not just influencers.
        <br><br>
        <span class="methodology-header">2. THE INTELLIGENCE (Gemini 2.0 Pro)</span>
        We employ <b>Google's Gemini 2.0 Pro</b> engine, tuned to understand Malaysian context (<i>Manglish, Bahasa Rojak, Dialects</i>). 
        It categorizes users into 4 key archetypes:
        <ul>
            <li><span class="methodology-sub">Economic Pragmatist:</span> Focuses on wallet issues (Wages, Prices).</li>
            <li><span class="methodology-sub">Urban Reformist:</span> Focuses on governance, corruption, and civil liberties.</li>
            <li><span class="methodology-sub">Heartland Conservative:</span> Focuses on tradition, religion, and rural identity.</li>
            <li><span class="methodology-sub">Digital Cynic:</span> Uses satire and memes to express disillusionment.</li>
        </ul>
        <br>
        <span class="methodology-header">3. THE METRICS</span>
        <span class="methodology-sub">Public Consensus:</span> The ratio of Positive to Total voices.<br>
        <span class="methodology-sub">Resistance Level:</span> The ratio of Negative to Total voices.<br>
        <span class="methodology-sub">Dominant Conversation:</span> The primary theme driving engagement (e.g., Cost of Living, Leadership).
        <br><br>
        <i>Disclaimer: This tool analyzes specific keywords and relies on generative AI interpretation. It is designed for trend analysis, not statistical polling.</i>
    </div>
    """, unsafe_allow_html=True)