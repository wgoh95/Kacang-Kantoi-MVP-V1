import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client

# 1. Setup
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("❌ Error: .env file missing.")
    exit()

supabase = create_client(url, key)

# 2. The Simulation Matrix (Psychographic Focus)
topics = [
    "Subsidy Rationalisation", 
    "Cost of Living", 
    "PADU Registration", 
    "Digital Economy", 
    "Corruption Crackdown", 
    "Healthcare Reform",
    "Exchange Rate (MYR/USD)"
]

# THE NEW MEANINGFUL CATEGORIES
personas = [
    "Economic Pragmatist", 
    "Heartland Conservative", 
    "Urban Reformist", 
    "Digital Cynic"
]

# Realistic "Voices" mapped to Archetypes
templates = [
    # Economic Pragmatist (Focus: Wallet & Business)
    {
        "persona": "Economic Pragmatist",
        "sentiment": "Negative",
        "raw": "SST increase to 8% is going to kill small businesses. Margins are already thin. #economy",
        "summary": "User worries that the SST hike will hurt SME profit margins."
    },
    {
        "persona": "Economic Pragmatist",
        "sentiment": "Positive",
        "raw": "Ringgit strengthening slightly against USD. Good sign for imports, hope it holds.",
        "summary": "User notes the strengthening Ringgit as a positive indicator for trade."
    },
    
    # Heartland Conservative (Focus: Tradition & Aid)
    {
        "persona": "Heartland Conservative",
        "sentiment": "Negative",
        "raw": "Why cut diesel subsidies? Farmers and fishermen rely on this daily. This hurts the kampung folks.",
        "summary": "User criticizes subsidy cuts for impacting rural livelihoods."
    },
    {
        "persona": "Heartland Conservative",
        "sentiment": "Positive",
        "raw": "Alhamdulillah, the new cash aid is helpful for B40 families before Raya.",
        "summary": "User expresses gratitude for government cash aid ahead of festivities."
    },

    # Urban Reformist (Focus: Governance & Competence)
    {
        "persona": "Urban Reformist",
        "sentiment": "Neutral",
        "raw": "PADU is a good idea on paper, but the data security implementation is worrying. We need better tech governance.",
        "summary": "User supports PADU's intent but questions its data privacy standards."
    },
    {
        "persona": "Urban Reformist",
        "sentiment": "Positive",
        "raw": "Finally, some real arrests by SPRM. No more double standards for VVIPs please.",
        "summary": "User applauds anti-corruption actions and demands equal justice."
    },

    # Digital Cynic (Focus: Hopelessness & Satire)
    {
        "persona": "Digital Cynic",
        "sentiment": "Negative",
        "raw": "New taxes, same old broken roads. Where is my tax money actually going? 🤡 #malaysia",
        "summary": "User uses sarcasm to highlight infrastructure failures despite tax hikes."
    },
    {
        "persona": "Digital Cynic",
        "sentiment": "Neutral",
        "raw": "Another U-turn on policy? At this point I'm just here for the memes.",
        "summary": "User expresses apathy and amusement at policy inconsistencies."
    }
]

print("🚀 Initializing Kacang Kantoi Simulation (Psychographic Mode)...")

# 3. Inject 50 Rows of Data
for i in range(50):
    # Pick a random base template to ensure Persona matches the Tone
    template = random.choice(templates)
    
    # Randomize Topic slightly (unless specific to template)
    topic = random.choice(topics)
    
    # Create a random timestamp within the last 48 hours
    random_minutes = random.randint(1, 2880)
    fake_time = (datetime.now() - timedelta(minutes=random_minutes)).isoformat()

    data = {
        "topic": topic,
        "sentiment": template["sentiment"],
        "persona": template["persona"], # Uses the correct matching persona
        "raw_comment": template["raw"],
        "summary": template["summary"],
        "created_at": fake_time
    }

    try:
        supabase.table("sentiment_logs").insert(data).execute()
        print(f"   [{i+1}/50] Signal: {template['persona']} on {topic}")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")

print("\n✅ Simulation Complete. Psychographic profiles updated.")