import os
import random
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Setup & Config
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: .env file missing. Cannot connect to Supabase.")
    exit()

supabase: Client = create_client(url, key)

# 2. SHARED LOGIC (Copied from sentiment_engine.py for consistency)
ARCHETYPE_WEIGHTS = {
    "Heartland Conservative": 2.5,
    "Economic Pragmatist": 1.5,
    "Urban Reformist": 1.0,
    "Digital Cynic": 0.5
}

def calculate_impact_score(sentiment_val, archetype, is_3r, velocity_score):
    """
    Calculates Political Impact Score (NTS).
    Formula: Sentiment * Archetype * Risk * VelocityBonus
    """
    weight = ARCHETYPE_WEIGHTS.get(archetype, 0.5)
    risk_multiplier = 1.5 if is_3r else 1.0
    velocity_bonus = 1.2 if velocity_score > 500 else 1.0
    
    return sentiment_val * weight * risk_multiplier * velocity_bonus

# 3. HIGH-FIDELITY TEMPLATES (The "Script")
print("🚀 Initializing Kacang Kantoi Simulation (v2.0 - Velocity Enabled)...")

templates = [
    # --- DOMAIN 1: ECONOMIC ANXIETY ---
    {
        "persona": "Economic Pragmatist",
        "domain": "Economic Anxiety",
        "trigger": "SST Hike",
        "sentiment": -1, # Negative
        "is_3r": False,
        "summary": "User complains that the SST hike is directly causing food price inflation."
    },
    {
        "persona": "Economic Pragmatist",
        "domain": "Economic Anxiety",
        "trigger": "Diesel Subsidy",
        "sentiment": -1,
        "is_3r": False,
        "summary": "Frustration with the technical implementation of the Budi Madani diesel portal."
    },
    {
        "persona": "Economic Pragmatist",
        "domain": "Economic Anxiety",
        "trigger": "Ringgit Recovery",
        "sentiment": 1, # Positive
        "is_3r": False,
        "summary": "Optimism about the strengthening Ringgit reducing import costs."
    },

    # --- DOMAIN 2: INSTITUTIONAL INTEGRITY ---
    {
        "persona": "Urban Reformist",
        "domain": "Institutional Integrity",
        "trigger": "MACC Action",
        "sentiment": 1,
        "is_3r": False,
        "summary": "Support for MACC's aggressive stance against high-profile corruption."
    },
    {
        "persona": "Urban Reformist",
        "domain": "Institutional Integrity",
        "trigger": "DNAA Decision",
        "sentiment": -1,
        "is_3r": False,
        "summary": "Criticism of the DNAA decision as a sign of legal bias favoring elites."
    },

    # --- DOMAIN 3: IDENTITY POLITICS (High Risk) ---
    {
        "persona": "Heartland Conservative",
        "domain": "Identity Politics",
        "trigger": "Vernacular Schools",
        "sentiment": -1,
        "is_3r": True, # RISK MULTIPLIER ACTIVE
        "summary": "Advocacy for single-stream education, citing vernacular schools as divisive."
    },
    {
        "persona": "Heartland Conservative",
        "domain": "Identity Politics",
        "trigger": "Halal Cert",
        "sentiment": 1,
        "is_3r": True,
        "summary": "Defense of strict Halal certification as non-negotiable for Muslim consumers."
    },

    # --- DOMAIN 4: PUBLIC COMPETENCY ---
    {
        "persona": "Digital Cynic",
        "domain": "Public Competency",
        "trigger": "PADU Glitch",
        "sentiment": -1,
        "is_3r": False,
        "summary": "Mockery of the government's digital transformation due to PADU errors."
    },

    # --- DOMAIN 5: POLITICAL MANEUVERING ---
    {
        "persona": "Digital Cynic",
        "domain": "Political Maneuvering",
        "trigger": "Coalition Drama",
        "sentiment": 0, # Neutral
        "is_3r": False,
        "summary": "Fatigue with constant political scheming and rumors of government toppling."
    }
]

# 4. INJECT 50 ROWS OF SYNTHETIC DATA
count = 0

print("⚙️  Generating synthetic traffic patterns...")

for i in range(50):
    # Pick a random template
    t = random.choice(templates)
    
    # Simulate Velocity: Random Views (100 to 500,000) & Random Age (1 to 24 hours)
    views = random.randint(100, 500000)
    age_hours = random.uniform(0.5, 24.0)
    
    # Calculate Velocity Score (Views / Hour)
    velocity_score = views / age_hours
    
    # Calculate Impact Score using REAL Engine Logic
    impact = calculate_impact_score(t["sentiment"], t["persona"], t["is_3r"], velocity_score)

    # Generate Timestamp
    fake_time = (datetime.now() - timedelta(hours=age_hours)).isoformat()

    # Construct Payload (Matching sentiment_logs schema)
    payload = {
        "video_id": f"sim_{random.randint(10000, 99999)}",
        "sentiment": t["sentiment"],
        "archetype": t["persona"],
        "topic": t["domain"],
        "specific_trigger": t["trigger"],
        "is_3r": t["is_3r"],
        "summary": t["summary"],
        "impact_score": impact,
        "created_at": fake_time
        # Note: We don't save 'velocity' or 'views' here because sentiment_logs 
        # usually doesn't store raw video stats, but the impact_score reflects it.
    }

    try:
        supabase.table("sentiment_logs").insert(payload).execute()
        count += 1
        print(f"✅ [{count}/50] Injected: {t['trigger']} (Vel: {int(velocity_score)}/hr) -> Score: {impact:.2f}")
    except Exception as e:
        print(f"⚠️ Error injecting row: {e}")

print(f"\n🎉 Simulation Complete. {count} rows added.")
print("👉 Run 'streamlit run app.py' to see the new Velocity-Weighted Impact Scores.")