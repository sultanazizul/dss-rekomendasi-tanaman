import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Warning: SUPABASE_URL or SUPABASE_KEY not found in environment variables.")
    # We might want to raise an error or handle this gracefully depending on if we are testing or running
    # For now, we'll let it fail if used.

def get_supabase_client() -> Client:
    if not url or not key:
        raise ValueError("Supabase credentials are missing. Please check your .env file.")
    return create_client(url, key)
