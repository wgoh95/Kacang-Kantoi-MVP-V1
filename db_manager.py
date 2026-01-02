import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment variables")

supabase: Client = create_client(supabase_url, supabase_key)


if __name__ == "__main__":
    try:
        # Test connection by attempting a simple query
        response = supabase.table("videos").select("*").limit(1).execute()
        print("\033[92m✅ Database Connected!\033[0m")
    except Exception as e:
        print(f"\033[91m❌ Connection failed: {e}\033[0m")
