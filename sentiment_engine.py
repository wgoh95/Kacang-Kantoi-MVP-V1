import os
import json
from google import genai
from google.genai import types
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Setup Gemini (New SDK) & Supabase
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Missing GEMINI_API_KEY")

client = genai.Client(api_key=gemini_api_key)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def generate_daily_brief():
    print("🗞️ Generating Daily Intelligence Brief (google-genai v1)...")

    try:
        # 1. Fetch last 24h of data (limit 200 for context window efficiency)
        response = supabase.table("sentiment_logs") \
            .select("topic, specific_trigger, sentiment, summary") \
            .order("created_at", desc=True) \
            .limit(200) \
            .execute()
        
        data = response.data
        if not data:
            print("⚠️ No data found to generate brief.")
            return

        # 2. The Editor Prompt
        prompt = f"""
        Here is a log of the last 200 political comments from Malaysia.
        Data: {json.dumps(data)}

        TASK:
        Identify the Top 3 "Dominant Conversations" driving public sentiment.
        Output JSON format with 'headline' and 'top_issues' list.
        """

        # --- NEW SDK CALL ---
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                response_mime_type="application/json"
            )
        )

        brief = json.loads(response.text.strip())

        # 3. Save to narrative_briefs
        supabase.table("narrative_briefs").insert({
            "content": brief
        }).execute()

        print("✅ Daily Brief Generated & Saved.")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    generate_daily_brief()