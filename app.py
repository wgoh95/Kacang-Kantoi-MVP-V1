import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 1. CONFIGURATION
st.set_page_config(
    page_title="KACANG KANTOI | The Memory Guard", 
    page_icon="🥜", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)
load_dotenv()

# 2. DESIGN SYSTEM (CSS)
st.markdown("""
<style>
    /* IMPORT FONTS: Rubik (Headlines) & Inter (Body) */
    @import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;700;900&family=Inter:wght@300;400;600;800&display=swap');

    /* GLOBAL RESET */
    .stApp { background-color: #050505; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2rem !important; padding-bottom: 5rem !important; }

    /* --- HERO CARD --- */
    .hero-card {
        background-color: #FFFFFF;
        border: 1px solid #222;
        border-left: 10px solid #FFC107; /* Brand Yellow */
        padding: 3rem;
        border-radius: 2px;
        margin-bottom: 2rem;
    }
    .hero-label {
        color: #FFC107; font-family: 'Rubik', sans-serif; font-weight: 700;
        letter-spacing: 2px; font-size: 0.9rem; text-transform: uppercase; margin-bottom: 10px;
    }
    .hero-title {
        font-family: 'Rubik', sans-serif; font-size: 4.5rem !important; font-weight: 900 !important;
        color: #000000 !important; text-transform: uppercase; line-height: 0.9;
    }
    .hero-title-highlight { color: #FFC107 !important; }
    .hero-copy {
        font-family: 'Inter', sans-serif; font-size: 1.15rem; color: #222; font-weight: 500;
        line-height: 1.6; margin-top: 1.5rem; max-width: 800px;
        border-left: 4px solid #000; padding-left: 20px;
    }

    /* --- METRICS --- */
    [data-testid="stMetricLabel"] {
        font-family: 'Rubik', sans-serif; color: #888; font-size: 0.8rem !important;
        text-transform: uppercase; letter-spacing: 1px; font-weight: 500;
    }
    [data-testid="stMetricValue"] {
        font-family: 'Rubik', sans-serif; color: #FFF; font-size: 2.5rem !important; font-weight: 700;
    }

    /* --- SIGNAL BOARD --- */
    .signal-title {
        font-family: 'Rubik', sans-serif; color: #FFF; font-size: 1rem; font-weight: 700; 
        text-transform: uppercase; margin-bottom: 10px; border-bottom: 2px solid #333; padding-bottom: 5px;
    }
    .signal-item {
        font-family: 'Inter', sans-serif; font-size: 0.9rem; color: #CCC; 
        margin-bottom: 5px; display: flex; justify-content: space-between;
    }
    .signal-score-pos { color: #00E396; font-weight: 700; }
    .signal-score-neg { color: #FF4560; font-weight: 700; }

    /* --- NARRATIVE BOX --- */
    .narrative-box {
        background-color: #111; 
        border: 1px solid #333; 
        border-left: 4px solid #FFC107;
        padding: 20px; 
        height: 100%;
        margin-top: -15px; 
    }
    .narrative-header {
        font-family: 'Rubik', sans-serif; color: #FFF; font-weight: 900; 
        text-transform: uppercase; font-size: 1.3rem; margin-bottom: 5px; letter-spacing: 0.5px;
    }
    .narrative-sub {
        font-family: 'Rubik', sans-serif; color: #FFC107; font-size: 0.75rem;
        text-transform: uppercase; letter-spacing: 2px; margin-bottom: 10px; font-weight: 700;
    }
    .narrative-text {
        font-family: 'Inter', sans-serif; color: #CCC; font-size: 1rem; line-height: 1.4; font-style: italic;
    }

    /* --- SPACER --- */
    .spacer { margin-top: 40px; }

    /* --- CHART HEADERS --- */
    h3 {
        font-family: 'Rubik', sans-serif; color: #FFF !important; text-transform: uppercase;
        font-weight: 900 !important; font-size: 2rem !important; margin-top: 50px !important;
        border-left: 6px solid #FFC107; padding-left: 15px;
    }
    .chart-caption {
        font-family: 'Inter', sans-serif; color: #888; font-size: 0.95rem; margin-bottom: 25px; margin-left: 22px; max-width: 650px;
    }

    /* --- CUSTOM TIME SELECTOR (THE TOGGLE BAR) --- */
    /* 1. Hide the label "Time Range:" */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    /* 2. Container Style */
    div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        gap: 8px;
        background-color: transparent;
        margin-left: 22px; /* Align with chart caption */
        margin-bottom: 10px;
    }
    /* 3. Hide the Radio Circles */
    div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    /* 4. Button Style */
    div[role="radiogroup"] label {
        background-color: #111 !important;
        border: 1px solid #333 !important;
        border-radius: 4px !important;
        padding: 6px 16px !important;
        margin: 0 !important;
        transition: all 0.2s ease-in-out;
    }
    div[role="radiogroup"] label:hover {
        border-color: #FFC107 !important;
        cursor: pointer;
    }
    /* 5. Text Style inside Button */
    div[role="radiogroup"] p {
        font-family: 'Rubik', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        color: #CCC !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    /* 6. Active State (Streamlit highlights text automatically, we enhance contrast) */
    div[role="radiogroup"] [data-checked="true"] + div p {
        color: #FFC107 !important;
    }
    
    /* --- METHODOLOGY --- */
    .methodology-header {
        color: #FFC107; font-family: 'Rubik'; text-transform: uppercase; margin-bottom: 5px; font-size: 1rem; margin-top: 20px;
    }
    .methodology-text {
        font-family: 'Inter'; color: #CCC; font-size: 0.95rem; line-height: 1.6; margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 3. INITIALIZE CONNECTION
@st.cache_resource
def init_connection():
    if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"):
        return None
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

supabase = init_connection()

# 4. DATA LOADING
def load_data(days_filter=1):
    if not supabase: return pd.DataFrame()
    try:
        cutoff_date = (datetime.utcnow() - timedelta(days=days_filter)).isoformat()
        response = supabase.table("sentiment_logs") \
            .select("created_at, sentiment, archetype, topic, summary, impact_score, specific_trigger, is_3r") \
            .gte("created_at", cutoff_date) \
            .order("created_at", desc=True) \
            .execute()
            
        df = pd.DataFrame(response.data)
        if df.empty: return df
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['impact_score'] = pd.to_numeric(df['impact_score'], errors='coerce').fillna(0)
        df['archetype'] = df['archetype'].fillna("Unknown")
        return df
    except Exception as e:
        return pd.DataFrame()

def load_intelligence():
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

# --- STATE ---
if 'time_range' not in st.session_state:
    st.session_state['time_range'] = 1

# --- HERO SECTION ---
st.markdown(f"""
<div class="hero-card">
    <div class="hero-label">OUR MISSION</div>
    <div class="hero-title">BEYOND THE <br><span class="hero-title-highlight">WAYANG.</span></div>
    <div class="hero-copy">
        <b>Kacang Kantoi</b> exists because Malaysian politics is theater. 
        While politicians rely on 3R distractions and short memories, we rely on <b>receipts</b>.
        <br><br>
        We are the nation's <b>Memory Guard</b>. We track the gap between what they say in Parliament and what you feel on the street.
        No jargon. No spin. Just the data.
        <br><br>
        <i>Simple. Snackable. Undeniable.</i>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SECTION HEADER ---
st.markdown("### THE REALITY CHECK")

# --- CUSTOM TIME SELECTOR (TOGGLE BAR) ---
# Placed directly under header, full width (no columns needed due to CSS styling)
time_option = st.radio(
    "Time Range:",
    ("24H", "3 Days", "7 Days", "30 Days", "3 Months"),
    horizontal=True,
    label_visibility="collapsed"
)

# LOGIC
time_map = {"24H": 1, "3 Days": 3, "7 Days": 7, "30 Days": 30, "3 Months": 90}
days_to_load = time_map[time_option]

df = load_data(days_to_load)
latest_intel = load_intelligence()

# CAPTION
st.markdown(f"<div class='chart-caption'>Audit of digital conversations over the last <b>{time_option}</b>.</div>", unsafe_allow_html=True)

if not df.empty:
    total_abs_impact = df['impact_score'].abs().sum()
    
    if total_abs_impact > 0:
        resistance_vol = df[df['impact_score'] < 0]['impact_score'].abs().sum()
        resistance_pct = (resistance_vol / total_abs_impact) * 100
        consensus_pct = 100 - resistance_pct
    else:
        resistance_pct = 0
        consensus_pct = 0
    
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.metric(
            "Voices Scanned", 
            len(df), 
            delta="Sample Size", 
            help="Total verified data points in the selected timeframe."
        )
    with m2:
        st.metric(
            "Approval Score", 
            f"{consensus_pct:.1f}%", 
            delta="Support",
            help="THE MANDATE: How much political capital the government has. >50% is safe."
        )
    with m3:
        st.metric(
            "Anger Level", 
            f"{resistance_pct:.1f}%", 
            delta="Friction", 
            delta_color="inverse",
            help="RESISTANCE: Active pushback and dissatisfaction intensity."
        )
    with m4:
        # NARRATIVE BOX
        if latest_intel:
            content = latest_intel['content']
            headline = content.get('headline', 'System Stable')
            narrative = content.get('public_narrative', content.get('dominant_narrative', 'Analyzing data streams...'))
            
            st.markdown(f"""
            <div class="narrative-box">
                <div class="narrative-sub">THE BOTTOM LINE</div>
                <div class="narrative-header">{headline}</div>
                <div class="narrative-text">"{narrative}"</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Initializing Analyst...")

    # --- SIGNAL BOARD ---
    st.markdown("<div class='spacer'></div>", unsafe_allow_html=True) 
    
    with st.expander(f"🔻 TAP TO SEE DRIVERS (LAST {time_option})", expanded=False):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.markdown('<div class="signal-title" style="color:#FF4560;">🔥 WHAT\'S BURNING (Issues)</div>', unsafe_allow_html=True)
            threats = df[df['impact_score'] < 0].groupby('specific_trigger')['impact_score'].sum().sort_values().head(5)
            for trigger, score in threats.items():
                st.markdown(f'<div class="signal-item"><span>{trigger}</span><span class="signal-score-neg">{score:.1f}</span></div>', unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="signal-title" style="color:#00E396;">🛡️ WHAT\'S WORKING (Wins)</div>', unsafe_allow_html=True)
            wins = df[df['impact_score'] > 0].groupby('specific_trigger')['impact_score'].sum().sort_values(ascending=False).head(5)
            for trigger, score in wins.items():
                st.markdown(f'<div class="signal-item"><span>{trigger}</span><span class="signal-score-pos">+{score:.1f}</span></div>', unsafe_allow_html=True)

        with c3:
            st.markdown('<div class="signal-title" style="color:#FFC107;">⚡ GOING VIRAL (Trending)</div>', unsafe_allow_html=True)
            velocity = df['specific_trigger'].value_counts().head(5)
            for trigger, count in velocity.items():
                st.markdown(f'<div class="signal-item"><span>{trigger}</span><span style="color:#FFF;">{count} posts</span></div>', unsafe_allow_html=True)

else:
    st.warning("Waiting for data stream...")

# --- VISUALIZATION ROW ---
col_charts_1, col_charts_2 = st.columns([1, 2])

with col_charts_1:
    st.markdown("### WHO IS TALKING?")
    st.markdown("<div class='chart-caption'><b>The Share of Voice.</b> Demographic split for the selected timeframe.</div>", unsafe_allow_html=True)
    
    if not df.empty:
        voice_data = df['archetype'].value_counts().reset_index()
        voice_data.columns = ['archetype', 'count']
        
        color_map = {
            "Digital Cynic": "#FFC107", "Urban Reformist": "#FFFFFF",
            "Heartland Conservative": "#FFA500", "Economic Pragmatist": "#808080",
            "Unknown": "#333333"
        }
        
        fig_donut = px.pie(voice_data, values='count', names='archetype', hole=0.6, color='archetype', color_discrete_map=color_map)
        fig_donut.update_layout(template="plotly_dark", showlegend=True, legend=dict(orientation="h", y=-0.2, font=dict(family="Rubik", size=11)), margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig_donut.update_traces(textinfo='percent', textfont=dict(family="Rubik", size=14))
        st.plotly_chart(fig_donut, use_container_width=True)

with col_charts_2:
    st.markdown("### THE HEATMAP")
    st.markdown("""
    <div class='chart-caption'>
        <b>Risk Radar.</b> Mapping volume vs sentiment.
        <br>🔴 <b>TOP LEFT:</b> High Volume + Anger (Danger).
        <br>🟢 <b>TOP RIGHT:</b> High Volume + Support (Safety).
    </div>
    """, unsafe_allow_html=True)
    
    if not df.empty:
        radar_data = df.groupby('topic').agg(
            volume=('topic', 'count'), 
            avg_sentiment=('impact_score', 'mean'),
            trigger=('specific_trigger', lambda x: x.mode()[0] if not x.mode().empty else "Various")
        ).reset_index()
        
        fig_radar = px.scatter(
            radar_data, x="volume", y="avg_sentiment", color="avg_sentiment", 
            size="volume", text="trigger", color_continuous_scale="RdYlGn", 
            range_color=[-2.5, 2.5], size_max=60
        )
        fig_radar.update_traces(textposition='top center', textfont=dict(family="Rubik", size=12, color="white"))
        fig_radar.update_layout(template="plotly_dark", xaxis_title="How Loud Is It?", yaxis_title="How Angry Are They?", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, font=dict(family="Rubik"))
        fig_radar.add_hline(y=0, line_width=1, line_dash="dash", line_color="#555")
        fig_radar.add_vline(x=radar_data['volume'].median(), line_width=1, line_dash="dash", line_color="#555")
        st.plotly_chart(fig_radar, use_container_width=True)

# --- TRAJECTORY ---
st.markdown("### TRAJECTORY OF TRUST")
st.markdown(f"<div class='chart-caption'><b>Trend over the last {time_option}.</b> <span style='color:#FF4560'>Red Band</span> = Crisis. <span style='color:#00E396'>Green Band</span> = Safe.</div>", unsafe_allow_html=True)

if not df.empty:
    if days_to_load <= 3:
        sample_rate = 'H'
    elif days_to_load <= 7:
        sample_rate = '4H'
    else:
        sample_rate = 'D'

    df_trend = df.set_index('created_at').resample(sample_rate)['impact_score'].mean().reset_index()
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=df_trend['created_at'], 
        y=df_trend['impact_score'], 
        mode='lines+markers', 
        line=dict(color='#FFC107', width=4), 
        marker=dict(size=6, color='#FFF', line=dict(width=2, color='#000')), 
        name='Trust Score'
    ))
    
    # Zones
    fig_trend.add_hrect(y0=-2.5, y1=-0.5, fillcolor="red", opacity=0.1, layer="below", line_width=0)
    fig_trend.add_hrect(y0=0.5, y1=2.5, fillcolor="green", opacity=0.1, layer="below", line_width=0)
    
    fig_trend.update_layout(
        template="plotly_dark", 
        yaxis_title="Net Trust Score", 
        yaxis_range=[-3, 3], 
        xaxis_title=None, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', 
        font=dict(family="Rubik"), 
        hovermode="x unified"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# --- EVIDENCE LOG ---
st.markdown("### THE EVIDENCE LOG")
st.markdown("<div class='chart-caption'>The receipts. This is the raw, unfiltered feed of what people are actually saying, verified by our system.</div>", unsafe_allow_html=True)
if not df.empty:
    feed_df = df[['created_at', 'topic', 'specific_trigger', 'archetype', 'impact_score', 'summary']].copy()
    st.dataframe(feed_df, use_container_width=True, column_config={"created_at": st.column_config.DatetimeColumn("Timestamp", format="D MMM, HH:mm"), "impact_score": st.column_config.NumberColumn("Impact", format="%.2f")}, hide_index=True)

# --- TRANSPARENCY REPORT ---
with st.expander("📁 TRANSPARENCY REPORT: HOW WE WORK"):
    st.markdown("""
<div class="methodology-text">
<h4 class="methodology-header">1. DATA SOURCE: TIKTOK INTELLIGENCE</h4>
We currently deploy a focused dragnet on <b>TikTok</b>, scanning Malaysian political discourse in Malay, English, and Mandarin. 
We target high-velocity content (viral videos) to capture the pulse of the youth and rural vote bank.
<br><br>

<h4 class="methodology-header">2. THE VOTER ARCHETYPES (Who We Track)</h4>
Not all noise is equal. We categorize voices into 4 buckets to weigh their political impact:
<ul>
    <li><b style="color:#FFA500">Heartland Conservative:</b> Rural, traditional, and religious voters. High political weight (The "Kingmakers").</li>
    <li><b style="color:#808080">Economic Pragmatist:</b> Urban/Semi-urban voters focused on cost of living, business, and taxes. Swing voters.</li>
    <li><b style="color:#FFFFFF">Urban Reformist:</b> Governance-focused voters who care about institutional reforms and civil liberties. Base support.</li>
    <li><b style="color:#FFC107">Digital Cynic:</b> Trolls, satirists, and disengaged youth. High volume, but low political capital (Noise).</li>
</ul>

<h4 class="methodology-header">3. THE ISSUE DOMAINS (What We Track)</h4>
Every signal is sorted into one of 5 "Battlefield Buckets":
<ul>
    <li><b>Economic Anxiety:</b> Prices, subsidies, taxes (SST), and survival issues.</li>
    <li><b>Institutional Integrity:</b> Corruption, MACC cases, legal fairness, and reforms.</li>
    <li><b>Identity Politics:</b> Race, Religion, and Royalty (3R) triggers.</li>
    <li><b>Public Competency:</b> Infrastructure failures (roads/floods) and service delivery.</li>
    <li><b>Political Maneuvering:</b> Elections, party hopping, and coalition drama.</li>
</ul>
    
<h4 class="methodology-header">4. NET TRUST SCORE (The Math)</h4>
How do we calculate the score?
<br><i>NTS = (Sentiment × Archetype Weight × Risk Multiplier)</i>
<br>A positive score means the government is building capital. A negative score means they are bleeding it.
<br><br>
<i>We do not predict the future. We audit the present.</i>
</div>
""", unsafe_allow_html=True)