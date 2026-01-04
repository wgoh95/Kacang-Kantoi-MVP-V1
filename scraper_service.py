import os
import json
import datetime
from dotenv import load_dotenv
from apify_client import ApifyClient
from supabase import create_client, Client

# 1. Setup & Config
load_dotenv()

# Initialize clients
apify_token = os.getenv("APIFY_TOKEN")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not apify_token:
    raise ValueError("Missing APIFY_TOKEN in environment variables")
if not supabase_url or not supabase_key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

supabase: Client = create_client(supabase_url, supabase_key)

# Configuration: Define your search targets here
SEARCH_CONFIG = {
    "searchQueries": ["Anwar Ibrahim", "Malaysia Madani", "Subsidi Diesel", "Padu"],
    "resultsPerPage": 50,
    "maxItems": 50,
    "sortType": 0,  # 0 = Relevance
}

def safe_int(value):
    """Safely converts 10K, 1.2M, or strings to integers."""
    if not value:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    
    # Handle strings like "10K", "1.5M"
    s = str(value).upper().strip()
    if 'K' in s:
        return int(float(s.replace('K', '')) * 1000)
    if 'M' in s:
        return int(float(s.replace('M', '')) * 1000000)
    if 'B' in s:
        return int(float(s.replace('B', '')) * 1000000000)
    
    # Remove non-numeric chars except digits
    s = ''.join(filter(str.isdigit, s))
    return int(s) if s else 0

def run_scraper():
    """Run the TikTok scraper using Apify and return the results."""
    client = ApifyClient(apify_token)

    run_input = {
        "resultsPerPage": SEARCH_CONFIG["resultsPerPage"],
        "searchQueries": SEARCH_CONFIG["searchQueries"],
        "maxItems": SEARCH_CONFIG["maxItems"]
    }

    print(f"🚀 Starting TikTok scraper for: {SEARCH_CONFIG['searchQueries']}...")
    
    # NOTE: Ensure "clockworks/tiktok-scraper" is the correct actor ID
    run = client.actor("clockworks/tiktok-scraper").call(run_input=run_input)

    if not run:
        print("❌ Scraper run failed to initialize.")
        return []

    print(f"✅ Scraper finished. Fetching results from dataset {run['defaultDatasetId']}...")

    items = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)

    print(f"📦 Collected {len(items)} raw items from Apify.")
    return items


def save_results(items):
    """Save scraped TikTok videos to Supabase."""
    if not items:
        print("⚠️ No items to save.")
        return 0

    print("💾 Saving to Supabase...")
    
    videos_saved = 0
    errors = 0

    for item in items:
        try:
            # 1. Safe Extraction & Type Conversion
            video_id = item.get('id')
            if not video_id:
                # Some scrapers return 'video_id' instead of 'id'
                video_id = item.get('video_id')
                if not video_id:
                    continue

            # Handle Date (Fallback to now if missing)
            created_at = item.get('createTimeISO')
            if not created_at:
                 # Try unix timestamp conversion
                 ts = item.get('createTime')
                 if ts:
                     created_at = datetime.datetime.fromtimestamp(ts).isoformat()
                 else:
                     created_at = datetime.datetime.now().isoformat()

            video_data = {
                "id": str(video_id),
                "caption": item.get('text', '') or item.get('desc', ''), # Handle 'text' vs 'desc'
                "views": safe_int(item.get('playCount', 0)),
                "share_count": safe_int(item.get('shareCount', 0)),
                "like_count": safe_int(item.get('diggCount', 0)),
                "comment_count": safe_int(item.get('commentCount', 0)),
                "created_at": created_at,
                "thumbnail_url": item.get('videoMeta', {}).get('coverUrl') or "",
                "author_handle": item.get('authorMeta', {}).get('name', 'unknown')
            }

            # 2. Upsert into Supabase
            supabase.table('videos').upsert(video_data).execute()
            videos_saved += 1

        except Exception as e:
            # Print specific error details
            if errors < 5: 
                print(f"  ⚠️ Error saving video {item.get('id', 'unknown')}: {e}")
            errors += 1

    print(f"\n📊 Summary:")
    print(f"   - Processed: {len(items)}")
    print(f"   - Saved/Updated: {videos_saved}")
    print(f"   - Errors: {errors}")
    
    if videos_saved > 0:
        print(f"\033[92m✅ Successfully synced {videos_saved} videos to database.\033[0m")
    
    return videos_saved


if __name__ == "__main__":
    try:
        # 1. Harvest Data
        items = run_scraper()

        # 2. Store Data
        save_results(items)
        
    except Exception as e:
        print(f"\033[91m❌ Critical Error: {e}\033[0m")