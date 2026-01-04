import os
import json
import time
from google import genai
from google.genai import types
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not GEMINI_API_KEY or not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ Missing API Keys. Check your .env file.")

# Initialize Clients (Using the NEW Google SDK)
client = genai.Client(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def generate_daily_brief():
    print("🗞️ Generating Strategic Intelligence Brief (v2)...")

    try:
        # 1. Fetch analyzed logs from the last 24h
        # CORRECTED: querying 'topic', not 'domain'
        response = supabase.table("sentiment_logs") \
            .select("topic, summary, archetype, sentiment, impact_score") \
            .order("created_at", desc=True) \
            .limit(300) \
            .execute()
        
        data = response.data
        if not data:
            print("⚠️ No data found. Please run 'sentiment_engine.py' first to generate logs.")
            return

        # 2. Calculate "Pulse" Metrics
        avg_score = sum(d['impact_score'] for d in data) / len(data) if len(data) > 0 else 0
        
        # 3. The "War Room" Prompt
        prompt = f"""
        CONTEXT:
        You are the Chief Strategy Officer for a Malaysian political party.
        Current Net Trust Score: {avg_score:.2f} (Scale: -2.5 to +2.5).
        
        RAW INTEL LOGS (Last 50 interactions):
        {json.dumps(data[:50])}

        TASK:
        Generate the "Daily Situation Report" for the dashboard.
        
        REQUIREMENTS:
        1. HEADLINE: 5 words max. Punchy.
        2. DOMINANT NARRATIVE: What is the #1 story driving the score? Use "Lao Gao" storytelling style.
        3. CRISIS CHECK: If the score is below -0.5, declare a CRISIS (true) and name the trigger.
        4. ACTION: One sentence of strategic advice.

        OUTPUT JSON ONLY:
        {{
            "headline": "String",
            "crisis_alert": (boolean),
            "dominant_narrative": "String",
            "key_driver": "String (The specific topic)",
            "actionable_advice": "String"
        }}
        """

        # Call Gemini 2.0 Flash
        response = client.models.generate_content(
            model='gemini-3.0-pro',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json"
            )
        )

        brief = json.loads(response.text.strip())

        # 4. Save to 'narrative_briefs' table
        payload = {
            "content": brief,
            "net_trust_score": avg_score,
            "created_at": time.strftime('%Y-%m-%dT%H:%M:%S')
        }
        
        supabase.table("narrative_briefs").insert(payload).execute()

        print("✅ Strategic Brief Generated Successfully!")
        print(f"   Headline: {brief['headline']}")
        print(f"   Score: {avg_score:.2f}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_daily_brief()