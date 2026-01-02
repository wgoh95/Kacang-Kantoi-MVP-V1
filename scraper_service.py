import os
import json
from dotenv import load_dotenv
from apify_client import ApifyClient
from supabase import create_client, Client

# Load environment variables
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


def run_scraper():
    """Run the TikTok scraper using Apify and return the results."""
    # Load configuration from JSON file
    with open('apify_config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Initialize Apify client
    client = ApifyClient(apify_token)

    # Run the TikTok scraper actor
    print("Starting TikTok scraper...")
    run = client.actor("clockworks/tiktok-scraper").call(run_input=config)

    # Fetch results from the dataset
    items = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)

    print(f"Scraped {len(items)} items")
    return items


def save_results(items):
    """Save scraped TikTok videos to Supabase."""
    if not items:
        print("No items to save")
        return 0

    videos_saved = 0

    for item in items:
        # Map fields from TikTok scraper to database schema (corrected based on raw_data_dump.json)
        video_data = {
            "id": item['id'],
            "caption": item.get('text', ''),
            "views": item.get('playCount', 0),
            "created_at": item.get('createTimeISO'),
            "share_count": item.get('shareCount', 0),
            "like_count": item.get('diggCount', 0),
            "thumbnail_url": item.get('videoMeta', {}).get('coverUrl')
        }

        # Skip if no ID
        if not video_data['id']:
            continue

        try:
            # Upsert into videos table (insert or update if exists)
            supabase.table('videos').upsert(video_data).execute()
            videos_saved += 1

        except Exception as e:
            print(f"Error saving video {video_data['id']}: {e}")

    # Informational note about comments
    print("\033[94mℹ️  Note: Comments data not present in search results. Saved Video Metadata only.\033[0m")

    return videos_saved


if __name__ == "__main__":
    try:
        # Run the scraper
        items = run_scraper()

        # Save results to database
        videos_count = save_results(items)

        # Print success message in green
        print(f"\033[92m✅ Mapped and Saved {videos_count} videos to Supabase.\033[0m")
    except Exception as e:
        print(f"\033[91m❌ Error: {e}\033[0m")
