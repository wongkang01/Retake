import os
from supabase import create_client, Client
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# You will need to add these to your .env file
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY

_supabase: Client = None

def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            logger.warning("Supabase credentials missing. Cloud storage will be disabled.")
            return None
        _supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _supabase
