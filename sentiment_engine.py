import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from supabase import create_client, Client

# 1. Setup & Config
load_dotenv()

# Initialize Gemini AI (New SDK)
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("Missing GEMINI_API_KEY in environment variables")

client = genai.Client(api_key=gemini_api_key)

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

supabase: Client = create_client(supabase_url, supabase_key)

# Weights for Net Trust Score Calculation
ARCHETYPE_WEIGHTS = {
    "Heartland Conservative": 2.5,
    "Economic Pragmatist": 1.5,
    "Urban Reformist": 1.0,
    "Digital Cynic": 0.5
}

def calculate_impact_score(sentiment_val, archetype, is_3r):
    """
    Calculates the Political Impact Score.
    """
    weight = ARCHETYPE_WEIGHTS.get(archetype, 1.0)
    risk = 1.5 if is_3r else 1.0
    return sentiment_val * weight * risk

def analyze_videos():
    """
    Analyze unanalyzed videos, prioritizing HIGH IMPACT (Viral) content first.
    Classifies content into 5 MECE Domains and extracts specific triggers.
    """
    
    print("🚀 Starting Sentiment Engine (MECE Protocol)...")
    print("Fetching high-impact unanalyzed videos...")
    
    try:
        # 1. Fetch UNPROCESSED videos (is_analyzed = False)
        # We fetch a buffer of 50 to ensure we have enough candidates
        response = supabase.table("videos") \
            .select("id, caption, views") \
            .eq("is_analyzed", False) \
            .order("views", desc=True) \
            .limit(50) \
            .execute()
            
        candidates = response.data
        
        # 2. Take the Top 20 Viral Candidates
        videos_to_analyze = candidates[:20]
        
        if not videos_to_analyze:
            print("💤 No new viral videos to analyze.")
            return

        print(f"🎯 Found {len(videos_to_analyze)} high-impact videos to analyze.")

    except Exception as e:
        print(f"❌ Error fetching videos: {e}")
        return

    processed_count = 0

    # 3. The Analysis Loop
    for video in videos_to_analyze:
        video_id = video['id']
        caption = video.get('caption', '')
        views = video.get('views', 0)
        
        # Skip empty captions (nothing to analyze)
        if not caption or len(caption.strip()) < 3:
            print(f"⏭️ Skipping {video_id} (empty/short caption)")
            # Mark as analyzed so we don't keep checking it
            supabase.table("videos").update({"is_analyzed": True}).eq("id", video_id).execute()
            continue

        print(f"\n🧠 Processing {video_id} ({views} views)...")

        # 4. The MECE System Prompt
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
        - Return an integer score: -1 (Negative), 0 (Neutral), 1 (Positive)

        STEP 5: 3R CHECK:
        - Is this strictly related to Race, Religion, or Royalty? (Boolean)

        Return strictly valid JSON:
        {{
            "sentiment_score": (integer: -1, 0, or 1),
            "domain": "String (One of the 5 Domains above)",
            "specific_trigger": "String",
            "persona": "String",
            "is_3r": boolean,
            "summary": "String (15-word journalistic summary of WHY)"
        }}
        """

        try:
            # Call Gemini (New SDK)
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3, 
                    response_mime_type="application/json"
                )
            )
            
            # Parse JSON
            try:
                result = json.loads(response.text.strip())
            except json.JSONDecodeError:
                print(f"⚠️ JSON Parse Error for {video_id}, skipping...")
                continue

            # Handle edge case where Gemini returns a list
            if isinstance(result, list):
                result = result[0] if len(result) > 0 else {}

            # Extract Values with defaults
            sent_score = int(result.get("sentiment_score", 0))
            archetype = result.get("persona", "Digital Cynic") # Default to Cynic if unknown
            is_3r = bool(result.get("is_3r", False))
            
            # Calculate Impact Score (NTS)
            impact = calculate_impact_score(sent_score, archetype, is_3r)

            # Map Data to Supabase Schema
            db_payload = {
                "video_id": video_id,
                "sentiment": sent_score,
                "archetype": archetype,
                "topic": result.get("domain", "Uncategorized"), # Map 'domain' to 'topic'
                "specific_trigger": result.get("specific_trigger", "General"), # Extra detail if you have a column for it
                "is_3r": is_3r,
                "summary": result.get("summary", ""),
                "impact_score": impact,
                "created_at": time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            
            # Insert into Supabase
            supabase.table("sentiment_logs").insert(db_payload).execute()
            
            # Mark video as analyzed
            supabase.table("videos").update({"is_analyzed": True}).eq("id", video_id).execute()
            
            print(f"✅ Analyzed: {db_payload['topic']} -> {db_payload['specific_trigger']}")
            print(f"   Persona: {db_payload['archetype']} | Impact Score: {impact}")
            processed_count += 1
            
        except Exception as e:
            print(f"❌ Error analyzing {video_id}: {e}")
            # Mark as analyzed anyway to prevent infinite loops on bad data
            supabase.table("videos").update({"is_analyzed": True}).eq("id", video_id).execute()
            # Sleep briefly to let the API cool down
            time.sleep(1)

    print(f"\n✅ Batch Complete. Processed {processed_count}/{len(videos_to_analyze)} videos.")

if __name__ == "__main__":
    analyze_videos()