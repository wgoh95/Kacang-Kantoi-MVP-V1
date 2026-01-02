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
# Using the stable flash model
model = genai.GenerativeModel('gemini-2.0-flash')

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

supabase: Client = create_client(supabase_url, supabase_key)

def analyze_videos():
    """Analyze unprocessed videos and extract sentiment with cultural persona detection."""
    
    print("Fetching unanalyzed videos...")
    
    try:
        # Get list of video IDs we have already analyzed
        existing_logs = supabase.table("sentiment_logs").select("video_id").execute()
        analyzed_ids = [row['video_id'] for row in existing_logs.data]
        
        # Get all videos from the main table
        all_videos_response = supabase.table("videos").select("id, caption").execute()
        
        # Filter: Only keep videos that are NOT in the analyzed list
        # Limit to 10 at a time to be safe with API limits
        videos_to_analyze = [v for v in all_videos_response.data if v['id'] not in analyzed_ids][:10]
        
        if not videos_to_analyze:
            print("No new videos to analyze.")
            return

        print(f"Found {len(videos_to_analyze)} unanalyzed videos")

    except Exception as e:
        print(f"Error fetching videos: {e}")
        return

    processed_count = 0

    # 2. The Analysis Loop
    for video in videos_to_analyze:
        video_id = video['id']
        caption = video.get('caption', '')
        
        if not caption:
            print(f"Skipping {video_id} (empty caption)")
            continue

        print(f"\nProcessing {video_id}...")

        # 3. The Prompt
        prompt = f"""
        Analyze this TikTok caption regarding Malaysian PM Anwar Ibrahim.
        Caption: "{caption}"

        Return strictly valid JSON with these keys:
        - sentiment: (String) "Positive", "Negative", or "Neutral"
        - sentiment_score: (Float) -1.0 (Negative) to 1.0 (Positive)
        - topic: (String) The main political topic (e.g. Cost of Living, Corruption, 3R, Leadership)
        - persona: (String) "Urban", "Rural", "Local Chinese", "International"
        - sarcasm: (Boolean) true or false
        - summary: (String) A 1-sentence summary
        """

        try:
            # Call Gemini
            response = model.generate_content(prompt)
            
            # Clean the response text (remove ```json ... ``` wrappers)
            cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
            result = json.loads(cleaned_text)

            # --- CRITICAL FIX: Explicit Data Mapping ---
            # This dictionary matches your Supabase columns EXACTLY.
            db_payload = {
                "video_id": video_id,
                "sentiment": result.get("sentiment", "Neutral"),
                "sentiment_score": result.get("sentiment_score", 0.0),
                "topic": result.get("topic", "Uncategorized"),
                "persona": result.get("persona", "Unknown"),
                "sarcasm_flag": result.get("sarcasm", False),
                "summary": result.get("summary", ""),
                "raw_comment": caption  # We save the caption here for reference
            }
            
            # Insert into Supabase
            supabase.table("sentiment_logs").insert(db_payload).execute()
            
            print(f"✅ Analyzed: {db_payload['sentiment']} | {db_payload['topic']}")
            print(f"   Persona: {db_payload['persona']}")
            processed_count += 1
            
        except Exception as e:
            print(f"❌ Error analyzing {video_id}: {e}")
            # Sleep briefly to let the API cool down
            time.sleep(1)

    print(f"\n✅ Successfully processed {processed_count}/{len(videos_to_analyze)} videos")

if __name__ == "__main__":
    analyze_videos()