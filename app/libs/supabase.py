from supabase import create_client, Client
from app.configs.env import env

supabase: Client = create_client(env["SUPABASE_URL"], env["SUPABASE_ANON_KEY"])