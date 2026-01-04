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
# UPDATED: Aligned with the new "Strict Hierarchy" categories for realistic distribution
topics = [
    "Cost of Living",      
    "Economy",             
    "Corruption",          
    "Reform",              
    "Malay Rights",        
    "Education",           
    "Leadership"           # Kept as a minority category
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
        "raw": "SST increase to 8% is killing small businesses. We can't survive these margins. #economy",
        "summary": "User worries that the SST hike will hurt SME profit margins."
    },
    {
        "persona": "Economic Pragmatist",
        "sentiment": "Positive",
        "raw": "Ringgit recovering to 4.3 is a good start. Hopefully import costs go down soon.",
        "summary": "User views the strengthening Ringgit as a positive sign for reducing costs."
    },
    
    # Heartland Conservative (Focus: Tradition & Aid)
    {
        "persona": "Heartland Conservative",
        "sentiment": "Negative",
        "raw": "Why disturb the diesel subsidy? Fishermen in the kampung are suffering. This isn't what we voted for.",
        "summary": "User criticizes subsidy cuts for negatively impacting rural livelihoods."
    },
    {
        "persona": "Heartland Conservative",
        "sentiment": "Positive",
        "raw": "Thank you PM for the extra cash aid before Raya. It really helps the B40 families.",
        "summary": "User expresses gratitude for government cash aid ahead of festivities."
    },

    # Urban Reformist (Focus: Governance & Competence)
    {
        "persona": "Urban Reformist",
        "sentiment": "Neutral",
        "raw": "The anti-corruption drive is good, but we need institutional reforms, not just arrests.",
        "summary": "User supports anti-corruption but demands deeper institutional changes."
    },
    {
        "persona": "Urban Reformist",
        "sentiment": "Positive",
        "raw": "Finally addressing the monopoly in rice imports. This is the structural change we needed.",
        "summary": "User applauds the government for breaking up economic monopolies."
    },

    # Digital Cynic (Focus: Hopelessness & Satire)
    {
        "persona": "Digital Cynic",
        "sentiment": "Negative",
        "raw": "Price of chicken goes down, price of everything else goes up. Magic show! 🤡 #malaysia",
        "summary": "User uses sarcasm to highlight that living costs feel unchanged despite announcements."
    },
    {
        "persona": "Digital Cynic",
        "sentiment": "Neutral",
        "raw": "Another committee formed to study the problem? Wake me up when something actually happens.",
        "summary": "User expresses apathy towards the formation of yet another government committee."
    }
]

print("🚀 Initializing Kacang Kantoi Simulation (Psychographic Mode)...")

# 3. Inject 50 Rows of Data
for i in range(50):
    # Pick a random base template to ensure Persona matches the Tone
    template = random.choice(templates)
    
    # Randomize Topic slightly (unless specific to template, logic here allows mixing)
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