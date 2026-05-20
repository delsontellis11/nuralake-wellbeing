import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

def capture_lead(name: str, intent: str, phone: str) -> str:
    """Upsert a lead. Phone is the deduplication key."""
    try:
        from supabase import create_client
        client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        data = {
            "name": name,
            "phone": phone,
            "intent": intent,
        }
        client.table("leads").upsert(data, on_conflict="phone").execute()
        return f"Lead captured: {name} — {intent}"
    except Exception as e:
        print(f"Lead capture error: {e}")
        return f"Lead noted: {name} — {intent} (DB not connected yet)"