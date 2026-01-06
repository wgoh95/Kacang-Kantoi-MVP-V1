import os
import json
import time
import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from supabase import create_client, Client

# 1. Setup & Config
load_dotenv()

# Initialize Gemini AI
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

# 2. STRICT Archetype Definitions & Weights
# The engine will FORCE any unknown label into "Digital Cynic"
ARCHETYPE_WEIGHTS = {
    "Heartland Conservative": 2.5,
    "Economic Pragmatist": 1.5,
    "Urban Reformist": 1.0,
    "Digital Cynic": 0.5
}

def calculate_impact_score(sentiment_val, archetype, is_3r, velocity_score):
    """
    Calculates Political Impact Score (NTS).
    Formula: Sentiment * Archetype * Risk * VelocityBonus
    """
    # 1. Base Weight
    weight = ARCHETYPE_WEIGHTS.get(archetype, 0.5) # Default to 0.5 (Cynic) if unknown
    
    # 2. Risk Multiplier (3R)
    risk_multiplier = 1.5 if is_3r else 1.0
    
    # 3. Velocity Multiplier (Viral Bonus)
    # If video is getting >500 views/hour, it is "Breaking News". Boost impact by 20%.
    velocity_bonus = 1.2 if velocity_score > 500 else 1.0
    
    return sentiment_val * weight * risk_multiplier * velocity_bonus

def analyze_videos():
    print("🚀 Starting Sentiment Engine (Smart Velocity Protocol)...")
    
    try:
        # STEP 1: FETCH CANDIDATES (Smart Triage)
        # We fetch 100 unprocessed videos to sort them locally by velocity
        response = supabase.table("videos") \
            .select("id, caption, views, created_at") \
            .eq("is_analyzed", False) \
            .order("created_at", desc=True) \
            .limit(100) \
            .execute()
            
        candidates = response.data
        if not candidates:
            print("💤 No new videos to analyze.")
            return

        # STEP 2: CALCULATE VIRAL VELOCITY (Views per Hour)
        # This solves the "Old Viral Video" problem.
        now = datetime.datetime.utcnow()
        scored_candidates = []
        
        for v in candidates:
            # Parse timestamp (Handle format variations)
            try:
                # Remove 'Z' for UTC parsing compatibility if needed
                ts_str = v['created_at'].replace('Z', '+00:00')
                upload_time = datetime.datetime.fromisoformat(ts_str)
            except ValueError:
                upload_time = datetime.datetime.utcnow() # Fallback

            # Calculate Age in Hours (Min 0.5h to avoid divide-by-zero)
            age_seconds = (now - upload_time.replace(tzinfo=None)).total_seconds()
            age_hours = max(age_seconds / 3600, 0.5)
            
            # Velocity = Views / Hours
            velocity = v['views'] / age_hours
            
            v['velocity_score'] = velocity
            scored_candidates.append(v)

        # Sort by Velocity (Fastest Moving First) & Pick Top 20
        scored_candidates.sort(key=lambda x: x['velocity_score'], reverse=True)
        videos_to_analyze = scored_candidates[:20]
        
        print(f"🎯 Selected Top {len(videos_to_analyze)} High-Velocity Videos.")

    except Exception as e:
        print(f"❌ Error fetching videos: {e}")
        return

    processed_count = 0

    # STEP 3: ANALYSIS LOOP
    for video in videos_to_analyze:
        video_id = video['id']
        caption = video.get('caption', '')
        velocity_score = video.get('velocity_score', 0)
        
        if not caption or len(caption.strip()) < 3:
            # Skip empty but mark as done
            supabase.table("videos").update({"is_analyzed": True}).eq("id", video_id).execute()
            continue

        print(f"\n🧠 Processing {video_id} (Vel: {int(velocity_score)}/hr)...")

        # STEP 4: THE PROMPT (With Conceptual Definitions & Sarcasm)
        prompt = f"""
        Analyze this Malaysian political TikTok caption.
        Caption: "{caption}"

        TASK 1: CLASSIFY DOMAIN (Pick ONE):
        
        1. "Economic Anxiety"
           - CONCEPT: Fear regarding financial stability, survival, and wealth preservation.
           - OPERATION: Mentions prices, subsidies (diesel/rice), taxes (SST/GST), EPF withdrawals, low wages, cost of living, or currency (MYR/USD).

        2. "Institutional Integrity"
           - CONCEPT: Trust in the fairness of the system, rule of law, and ethical governance.
           - OPERATION: Mentions corruption, MACC (SPRM), court cases (DNAA), legal reforms, police misconduct, or cabinet appointments.

        3. "Identity Politics" (High Risk)
           - CONCEPT: Threats to group identity, cultural dominance, or religious sanctity.
           - OPERATION: Mentions Race (Malay/Chinese/Indian), Religion (Islam/Halal/Kafir), Royalty (3R), Language (Bahasa/Mandarin), or Vernacular Schools.

        4. "Public Competency"
           - CONCEPT: The government's ability to deliver basic services and infrastructure.
           - OPERATION: Mentions potholes, floods, healthcare waiting times, education quality, public transport (LRT/MRT), or digital failures (PADU/MySejahtera).

        5. "Political Maneuvering"
           - CONCEPT: The "Game" of politics—power struggles, popularity, and elections.
           - OPERATION: Mentions elections (PRK/PRU), polls, coalitions (PH/PN/BN), MP defections, or party drama without specific policy substance.

        TASK 2: ASSIGN PERSONA (Strictly Pick ONE):
        - "Heartland Conservative" (Rural/Religious/Tradition focus)
        - "Economic Pragmatist" (Business/Cost of Living/Middle Class focus)
        - "Urban Reformist" (Governance/Human Rights/Liberal focus)
        - "Digital Cynic" (Satire/Trolling/Hopelessness/Memes)
        *IF UNCLEAR, DEFAULT TO "Digital Cynic". DO NOT INVENT NEW LABELS.*

        TASK 3: DETECT SARCASM:
        - Boolean: True if the text says one thing but implies the opposite (e.g. "Hebat sangat PMX" on a video of a disaster).

        TASK 4: SENTIMENT:
        - Integer: -1 (Negative), 0 (Neutral), 1 (Positive).
        - IMPORTANT: If Sarcasm is True, INVERT the literal sentiment (Positive becomes Negative).

        TASK 5: 3R CHECK:
        - Boolean: True if specific to Race, Religion, or Royalty.

        TASK 6: TRIGGER:
        - Specific keyword driving the issue (max 4 words). E.g., "Diesel Subsidy", "SST Rate", "PADU Glitch".

        TASK 7: SUMMARY:
        - 15-word journalistic summary of the issue.

        OUTPUT JSON:
        {{
            "domain": "String",
            "persona": "String",
            "sentiment_score": Int,
            "is_sarcasm": Bool,
            "is_3r": Bool,
            "specific_trigger": "String",
            "summary": "String"
        }}
        """

        try:
            # Call Gemini
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2, # Low temp for strict adherence to definitions
                    response_mime_type="application/json"
                )
            )
            
            # Parse Logic
            try:
                result = json.loads(response.text.strip())
            except:
                print(f"⚠️ JSON Parse Error for {video_id}, skipping...")
                continue
            
            if isinstance(result, list): result = result[0]

            # STRICT BUCKETING ENFORCER
            # This fixes "Hallucinated Categories" by forcing unknowns to "Digital Cynic"
            raw_archetype = result.get("persona", "Digital Cynic")
            if raw_archetype not in ARCHETYPE_WEIGHTS:
                archetype = "Digital Cynic"
            else:
                archetype = raw_archetype

            # Calculate Scores
            sent_score = int(result.get("sentiment_score", 0))
            is_3r = bool(result.get("is_3r", False))
            
            impact = calculate_impact_score(sent_score, archetype, is_3r, velocity_score)

            # Save to DB
            db_payload = {
                "video_id": video_id,
                "sentiment": sent_score,
                "archetype": archetype,
                "topic": result.get("domain", "Uncategorized"),
                "specific_trigger": result.get("specific_trigger", "General"),
                "is_3r": is_3r,
                "summary": result.get("summary", ""),
                "impact_score": impact,
                "created_at": time.strftime('%Y-%m-%dT%H:%M:%S')
            }
            
            supabase.table("sentiment_logs").insert(db_payload).execute()
            supabase.table("videos").update({"is_analyzed": True}).eq("id", video_id).execute()
            
            print(f"✅ Saved: {archetype} ({db_payload['topic']}) | Score: {impact:.2f}")
            processed_count += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")
            # Mark as analyzed anyway to prevent infinite loops on bad data
            supabase.table("videos").update({"is_analyzed": True}).eq("id", video_id).execute()
            time.sleep(1)

    print(f"\n✅ Batch Complete: {processed_count} videos.")

if __name__ == "__main__":
    analyze_videos()