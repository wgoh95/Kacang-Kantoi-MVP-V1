import os
import json
import time
from datetime import datetime, timedelta
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

client = genai.Client(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_average_score(start_time, end_time):
    """Calculates average impact score for a specific time window."""
    try:
        response = supabase.table("sentiment_logs") \
            .select("impact_score") \
            .gte("created_at", start_time) \
            .lt("created_at", end_time) \
            .execute()
        
        scores = [d['impact_score'] for d in response.data if d.get('impact_score') is not None]
        return sum(scores) / len(scores) if scores else 0.0
    except:
        return 0.0

def generate_daily_brief():
    print("🗞️ Generating 'Memory Guard' Intelligence Audit...")

    try:
        # 1. TIME TRAVEL (The Unblinking Record)
        now = datetime.utcnow()
        one_day_ago = (now - timedelta(days=1)).isoformat()
        two_days_ago = (now - timedelta(days=2)).isoformat()
        seven_days_ago = (now - timedelta(days=7)).isoformat()
        
        # Calculate The Reality Gap (Trends)
        current_score = get_average_score(one_day_ago, now.isoformat())
        yesterday_score = get_average_score(two_days_ago, one_day_ago)
        last_week_score = get_average_score((now - timedelta(days=8)).isoformat(), seven_days_ago)

        # 2. FILTERING THE "WAYANG" (Polarity Protocol)
        response = supabase.table("sentiment_logs") \
            .select("topic, specific_trigger, summary, archetype, sentiment, impact_score") \
            .order("created_at", desc=True) \
            .limit(1000) \
            .execute()
        
        data = response.data
        if not data: return

        # Extract "Signals" from "Noise"
        top_threats = sorted(data, key=lambda x: x['impact_score'] or 0)[:8]
        top_wins = sorted(data, key=lambda x: x['impact_score'] or 0, reverse=True)[:8]
        briefing_packet = top_threats + top_wins

        # 3. THE "MEMORY GUARD" PROMPT
        prompt = f"""
        CONTEXT:
        You are the "Memory Guard" for Kacang Kantoi.
        
        OUR MANIFESTO:
        "Malaysian politics is a lot of theater (Wayang). Politicians rely on short memories; we rely on forensic data.
        We bridge the gap between political theater and ground reality. 
        Make it KACANG: Simple, Snackable, Undeniable."
        
        THE AUDIT (Data Telemetry):
        - Current Trust Score: {current_score:.2f} (Scale: -2.5 to +2.5)
        - Gap vs Yesterday: {current_score - yesterday_score:.2f}
        - Gap vs Last Week: {current_score - last_week_score:.2f}
        
        EVIDENCE LOGS (Top Signals):
        {json.dumps(briefing_packet)}

        TASK:
        Write the "Daily Situation Report" that exposes the "So What."

        TONE & WRITING STYLE:
        1. **Beyond the Wayang:** Do not just report the news. Contrast the "Official Narrative" (what the government wants) vs. "Ground Reality" (what the data shows).
        2. **Rakyat Impact:** Focus on the "Wallet" and the "Daily Grind." If the score is down, it's not because of "bad PR," it's because "the rakyat is feeling pain."
        3. **Undeniable & Snackable:** Use short, punchy sentences. No academic fluff. "The rhetoric says recovery. The data says anxiety."
        4. **Memory Guard:** Explicitly mention if the current trend contradicts previous trends (using the Gap data).

        OUTPUT REQUIREMENTS:
        1. HEADLINE: 5 words max. Punchy. (e.g. "Wayang Fails: Diesel Anxiety Real").
        2. PUBLIC_NARRATIVE: 2-3 sentences. The "Simple, Snackable" story of the day. Reveal the gap between rhetoric and reality.
        3. PRIVATE_MEMO (Hidden): 1 sentence of brutal "So What" advice for the client. 

        OUTPUT JSON ONLY:
        {{
            "headline": "String",
            "public_narrative": "String",
            "private_memo": "String",
            "key_driver": "String"
        }}
        """

        # Call Gemini
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.45, # Higher creativity for that "Copywriter" flair
                response_mime_type="application/json"
            )
        )

        try:
            brief = json.loads(response.text.strip())
        except:
            clean_text = response.text.replace('```json', '').replace('```', '')
            brief = json.loads(clean_text)

        # 4. Save to Database
        payload = {
            "content": brief,
            "net_trust_score": current_score,
            "created_at": time.strftime('%Y-%m-%dT%H:%M:%S')
        }
        
        supabase.table("narrative_briefs").insert(payload).execute()

        print("✅ Memory Guard Audit Complete.")
        print(f"   Headline: {brief['headline']}")
        print(f"   Reality Check: {brief['public_narrative']}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_daily_brief()