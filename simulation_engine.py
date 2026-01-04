import os
import random
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

# 2. The Simulation Matrix (MECE Protocol)
print("🚀 Initializing Kacang Kantoi Simulation (MECE Protocol)...")

# The 5 Mutually Exclusive Domains
domains = [
    "Economic Anxiety", 
    "Institutional Integrity", 
    "Identity Politics", 
    "Public Competency", 
    "Political Maneuvering"
]

# High-fidelity templates to mimic real Malaysian discourse
templates = [
    # --- DOMAIN 1: ECONOMIC ANXIETY (The Wallet) ---
    {
        "persona": "Economic Pragmatist",
        "domain": "Economic Anxiety",
        "trigger": "SST Hike",
        "sentiment": "Negative",
        "raw": "SST naik 8% is killing the small hawkers. My teh tarik price went up again.",
        "summary": "User complains that the SST hike is directly causing food price inflation."
    },
    {
        "persona": "Economic Pragmatist",
        "domain": "Economic Anxiety",
        "trigger": "Diesel Subsidy",
        "sentiment": "Negative",
        "raw": "Applying for the diesel subsidy is so mess. The Budi Madani portal keeps crashing.",
        "summary": "User expresses frustration with the technical implementation of the diesel subsidy portal."
    },
    {
        "persona": "Economic Pragmatist",
        "domain": "Economic Anxiety",
        "trigger": "Ringgit Recovery",
        "sentiment": "Positive",
        "raw": "Good to see MYR strengthening against USD. Hopefully imported goods become cheaper soon.",
        "summary": "User views the strengthening Ringgit as a positive sign for reducing import costs."
    },

    # --- DOMAIN 2: INSTITUTIONAL INTEGRITY (The Law) ---
    {
        "persona": "Urban Reformist",
        "domain": "Institutional Integrity",
        "trigger": "MACC Action",
        "sentiment": "Positive",
        "raw": "Finally MACC is biting the big sharks. Don't just catch the ikan bilis.",
        "summary": "User supports the anti-corruption agency's move to target high-profile individuals."
    },
    {
        "persona": "Urban Reformist",
        "domain": "Institutional Integrity",
        "trigger": "DNAA Decision",
        "sentiment": "Negative",
        "raw": "Another DNAA? The legal system feels like a revolving door for the rich.",
        "summary": "User criticizes the Discharge Not Amounting to Acquittal (DNAA) as a sign of legal bias."
    },

    # --- DOMAIN 3: IDENTITY POLITICS (The Soul) ---
    {
        "persona": "Heartland Conservative",
        "domain": "Identity Politics",
        "trigger": "Vernacular Schools",
        "sentiment": "Negative",
        "raw": "We need one school stream for unity. Vernacular schools divide us from young.",
        "summary": "User advocates for a single-stream education system to promote national unity."
    },
    {
        "persona": "Heartland Conservative",
        "domain": "Identity Politics",
        "trigger": "Halal Cert",
        "sentiment": "Positive",
        "raw": "Strict Halal certification is necessary to protect Muslim consumers. No compromise.",
        "summary": "User defends strict Halal certification processes as essential for religious compliance."
    },

    # --- DOMAIN 4: PUBLIC COMPETENCY (The System) ---
    {
        "persona": "Digital Cynic",
        "domain": "Public Competency",
        "trigger": "PADU Glitch",
        "sentiment": "Negative",
        "raw": "Spent 1 hour on PADU just to get 'Error 404'. Digital transformation my foot.",
        "summary": "User mocks the government's digital initiatives due to technical failures during registration."
    },
    {
        "persona": "Urban Reformist",
        "domain": "Public Competency",
        "trigger": "Public Transport",
        "sentiment": "Positive",
        "raw": "The new MRT line is actually very convenient. Saves me 40 mins jam to KL.",
        "summary": "User praises the efficiency and convenience of the new public transport infrastructure."
    },

    # --- DOMAIN 5: POLITICAL MANEUVERING (The Game) ---
    {
        "persona": "Digital Cynic",
        "domain": "Political Maneuvering",
        "trigger": "Coalition Drama",
        "sentiment": "Neutral",
        "raw": "Rumors of another Dubai Move? Can these MPs just work instead of plotting?",
        "summary": "User expresses fatigue with constant political scheming and rumors of government toppling."
    },
    {
        "persona": "Heartland Conservative",
        "domain": "Political Maneuvering",
        "trigger": "By-Election",
        "sentiment": "Positive",
        "raw": "The massive win in Kemaman shows the people reject the liberal agenda.",
        "summary": "User interprets a by-election victory as a rejection of liberal policies."
    }
]

# 3. Inject 50 Rows of Synthetic Data
count = 0
for i in range(50):
    # Pick a random template
    template = random.choice(templates)
    
    # Generate random timestamp within last 24 hours (Real-time Simulation)
    random_minutes = random.randint(1, 1440) 
    fake_time = (datetime.now() - timedelta(minutes=random_minutes)).isoformat()

    # Construct Payload matching the Schema
    payload = {
        "video_id": f"sim_{random.randint(10000, 99999)}", # Fake ID
        "topic": template["domain"],          # The MECE Domain
        "specific_trigger": template["trigger"], # The specific issue
        "sentiment": template["sentiment"],
        "sentiment_score": 0.9 if template["sentiment"] == "Positive" else -0.9 if template["sentiment"] == "Negative" else 0.0,
        "persona": template["persona"],
        "raw_comment": template["raw"],
        "summary": template["summary"],
        "sarcasm_flag": True if template["persona"] == "Digital Cynic" else False,
        "created_at": fake_time
    }

    try:
        supabase.table("sentiment_logs").insert(payload).execute()
        count += 1
        print(f"✅ [{count}/50] Injected: {template['domain']} -> {template['trigger']}")
    except Exception as e:
        print(f"⚠️ Error injecting row: {e}")

print(f"\n🎉 Simulation Complete. {count} rows added to Supabase.")
print("👉 You can now run 'app.py' to see the dashboard light up.")