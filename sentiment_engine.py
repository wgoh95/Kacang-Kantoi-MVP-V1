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
    "temperature": 0.3, # Lower temperature for more consistent classification
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,
    "response_mime_type": "application/json",
}

# Using the stable flash model for speed and cost-efficiency
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
    Classifies content into 5 MECE Domains and extracts specific triggers.
    """
    
    print("🚀 Starting Sentiment Engine (MECE Protocol)...")
    print("Fetching high-impact unanalyzed videos...")
    
    try:
        # 1. Get list of video IDs we have already analyzed
        # We check the 'video_id' column in sentiment_logs to avoid re-processing
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
            print("💤 No new viral videos to analyze.")
            return

        print(f"🎯 Found {len(videos_to_analyze)} high-impact videos to analyze.")

    except Exception as e:
        print(f"❌ Error fetching videos: {e}")
        return

    processed_count = 0

    # 2. The Analysis Loop
    for video in videos_to_analyze:
        video_id = video['id']
        caption = video.get('caption', '')
        views = video.get('views', 0)
        
        # Skip empty captions (nothing to analyze)
        if not caption or len(caption.strip()) < 3:
            print(f"⏭️ Skipping {video_id} (empty/short caption)")
            continue

        print(f"\n🧠 Processing {video_id} ({views} views)...")

        # 3. The MECE System Prompt
        prompt = f"""
        Analyze this Malaysian political TikTok caption.
        Caption: "{caption}"

        Your task is to classify this content into ONE of 5 Mutually Exclusive domains.

        STEP 1: ASSIGN DOMAIN (Pick ONE only):
        1. "Economic Anxiety": Mentions prices, subsidies (diesel/rice/chicken), taxes (SST/GST), EPF, wages, cost of living, or currency (MYR/USD).
        2. "Institutional Integrity": Mentions corruption, MACC, court cases, DNAA, laws, reforms, police, or cabinet appointments.
        3. "Identity Politics": Mentions Race (Malay/Chinese/Indian), Religion (Islam/Halal), Royalty (3R), Language, or Vernacular Schools.
        4. "Public Competency": Mentions infrastructure (roads/floods), healthcare, education quality, transport, or system failures (PADU/MySejahtera).
        5. "Political Maneuvering": Mentions elections, polls, party coalitions (PH/PN/BN), MP defections, or politician popularity/drama with NO specific policy mention.

        STEP 2: IDENTIFY SPECIFIC TRIGGER:
        - What specific keyword drove this? (e.g., "Diesel Subsidy", "BlackRock Deal", "PADU Glitch", "SST Hike").
        - Keep it under 4 words.

        STEP 3: ASSIGN PERSONA (Psychographic):
        - "Economic Pragmatist" (Wallet/Business focus)
        - "Heartland Conservative" (Tradition/Rural/Religion focus)
        - "Urban Reformist" (Governance/Rights focus)
        - "Digital Cynic" (Satire/Hopelessness/Trolling)

        STEP 4: DETERMINE SENTIMENT:
        - "Positive" (Supportive of the subject)
        - "Negative" (Critical/Opposed)
        - "Neutral" (Factual/Unclear)

        Return strictly valid JSON:
        {{
            "sentiment": "String",
            "sentiment_score": float (-1.0 to 1.0),
            "domain": "String (One of the 5 Domains above)",
            "specific_trigger": "String",
            "persona": "String",
            "sarcasm": boolean,
            "summary": "String (15-word journalistic summary of WHY)"
        }}
        """

        try:
            # Call Gemini
            response = model.generate_content(prompt)
            
            # Clean and parse JSON (Handle Markdown wrapping)
            cleaned_text = response.text.replace("```json", "").replace("```", "").strip()
            
            try:
                result = json.loads(cleaned_text)
            except json.JSONDecodeError:
                print(f"⚠️ JSON Parse Error for {video_id}, skipping...")
                continue

            # Handle edge case where Gemini returns a list
            if isinstance(result, list):
                result = result[0] if len(result) > 0 else {}

            # Map Data to Supabase Schema
            # Note: We map 'domain' from JSON to 'topic' column in DB to match your schema
            db_payload = {
                "video_id": video_id,
                "sentiment": result.get("sentiment", "Neutral"),
                "sentiment_score": result.get("sentiment_score", 0.0),
                "topic": result.get("domain", "Uncategorized"), # Mapped to MECE Domain
                "specific_trigger": result.get("specific_trigger", "General"),
                "persona": result.get("persona", "Unknown"),
                "sarcasm_flag": result.get("sarcasm", False),
                "summary": result.get("summary", ""),
                "raw_comment": caption
            }
            
            # Insert into Supabase
            supabase.table("sentiment_logs").insert(db_payload).execute()
            
            print(f"✅ Analyzed: {db_payload['topic']} -> {db_payload['specific_trigger']}")
            print(f"   Persona: {db_payload['persona']} | Sentiment: {db_payload['sentiment']}")
            processed_count += 1
            
        except Exception as e:
            print(f"❌ Error analyzing {video_id}: {e}")
            # Sleep briefly to let the API cool down if we hit a rate limit
            time.sleep(2)

    print(f"\n✅ Batch Complete. Processed {processed_count}/{len(videos_to_analyze)} videos.")

if __name__ == "__main__":
    analyze_videos()