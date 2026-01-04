import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client, Client

# 1. Setup & Config
load_dotenv()

# Initialize Gemini AI
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Missing GEMINI_API_KEY in environment variables")

genai.configure(api_key=gemini_api_key)

# Configuration to force JSON output
generation_config = {
    "temperature": 0.4,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
    "response_mime_type": "application/json",
}

# Using the stable flash model
model = genai.GenerativeModel(
    model_name='gemini-2.0-flash',
    generation_config=generation_config
)

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

supabase: Client = create_client(supabase_url, supabase_key)

def analyze_videos():
    """
    Analyze unanalyzed videos, prioritizing HIGH IMPACT (Viral) content first.
    Extracts sentiment, topic, and persona using strict hierarchical rules.
    """
    
    print("Fetching high-impact unanalyzed videos...")
    
    try:
        # 1. Get list of video IDs we have already analyzed
        existing_logs = supabase.table("sentiment_logs").select("video_id").execute()
        analyzed_ids = {row['video_id'] for row in existing_logs.data} # Use set for faster lookup
        
        # 2. Fetch UNPROCESSED videos, sorted by VIEWS (Highest First)
        # We fetch a buffer of 50 to ensure we have enough candidates after filtering
        response = supabase.table("videos") \
            .select("id, caption, views") \
            .order("views", desc=True) \
            .limit(50) \
            .execute()
            
        # 3. Filter out the ones we've already done
        candidates = [v for v in response.data if v['id'] not in analyzed_ids]
        
        # 4. Take the Top 20 Viral Candidates
        videos_to_analyze = candidates[:20]
        
        if not videos_to_analyze:
            print("No new viral videos to analyze.")
            return

        print(f"Found {len(videos_to_analyze)} high-impact videos to analyze.")

    except Exception as e:
        print(f"Error fetching videos: {e}")
        return

    processed_count = 0

    # 2. The Analysis Loop
    for video in videos_to_analyze:
        video_id = video['id']
        caption = video.get('caption', '')
        views = video.get('views', 0)
        
        if not caption:
            print(f"Skipping {video_id} (empty caption)")
            continue

        print(f"\nProcessing {video_id} ({views} views)...")

        # 3. The Prompt (Updated with Strict Hierarchy)
        prompt = f"""
        Analyze this TikTok caption regarding Malaysian PM Anwar Ibrahim.
        Caption: "{caption}"

        You are a political analyst. Your task is to categorize this content with STRICT hierarchical rules.

        CRITICAL CATEGORIZATION RULES (Hierarchy):
        1. SPECIFIC POLICY: If the text mentions subsidies, diesel, rice, taxes (SST/GST), EPF, or prices -> Topic MUST be "Cost of Living" or "Economy".
        2. GOVERNANCE: If the text mentions corruption, MACC, court cases, or laws -> Topic MUST be "Corruption" or "Reform".
        3. SOCIAL: If the text mentions 3R (Race, Religion, Royalty), language, or schools -> Topic MUST be "Malay Rights", "Religion", or "Education".
        4. LEADERSHIP (Last Resort): ONLY use "Leadership" if the text is purely about the politician's popularity, image, or political moves with NO specific policy mention.

        Classify the user into ONE of these 4 specific Malaysian archetypes:
        1. "Economic Pragmatist" (Focus: Cost of living, wages, business, taxes)
        2. "Heartland Conservative" (Focus: Malay rights, Islam, tradition, rural subsidies)
        3. "Urban Reformist" (Focus: Corruption, reforms, institutional competency, civil liberties)
        4. "Digital Cynic" (Focus: Hopelessness, satire, anti-establishment memes)

        Return strictly valid JSON with these keys:
        - sentiment: (String) "Positive", "Negative", or "Neutral"
        - sentiment_score: (Float) -1.0 (Negative) to 1.0 (Positive)
        - topic: (String) The specific policy topic based on the hierarchy above.
        - persona: (String) One of the 4 archetypes listed above.
        - sarcasm: (Boolean) true or false
        - summary: (String) A 1-sentence summary of the user's main point.
        """

        try:
            # Call Gemini
            response = model.generate_content(prompt)
            
            # Clean and parse JSON
            cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
            
            try:
                result = json.loads(cleaned_text)
            except json.JSONDecodeError:
                print(f"⚠️ JSON Parse Error for {video_id}, skipping...")
                continue

            # Fix: If Gemini returns a List instead of an Object, grab the first item
            if isinstance(result, list):
                if len(result) > 0:
                    result = result[0]
                else:
                    result = {}

            # Map Data
            db_payload = {
                "video_id": video_id,
                "sentiment": result.get("sentiment", "Neutral"),
                "sentiment_score": result.get("sentiment_score", 0.0),
                "topic": result.get("topic", "Uncategorized"),
                "persona": result.get("persona", "Unknown"),
                "sarcasm_flag": result.get("sarcasm", False),
                "summary": result.get("summary", ""),
                "raw_comment": caption
            }
            
            # Insert into Supabase
            supabase.table("sentiment_logs").insert(db_payload).execute()
            
            print(f"✅ Analyzed: {db_payload['sentiment']} | {db_payload['topic']}")
            print(f"   Persona: {db_payload['persona']}")
            processed_count += 1
            
        except Exception as e:
            print(f"❌ Error analyzing {video_id}: {e}")
            # Sleep briefly to let the API cool down
            time.sleep(2)

    print(f"\n✅ Successfully processed {processed_count}/{len(videos_to_analyze)} high-impact videos")

if __name__ == "__main__":
    analyze_videos()