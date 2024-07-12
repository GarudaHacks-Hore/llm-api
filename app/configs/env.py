from dotenv import load_dotenv, dotenv_values

load_dotenv()
config = dotenv_values(".env")

env = {
    "SUPABASE_ANON_KEY": config["SUPABASE_ANON_KEY"] or "",
    "SUPABASE_URL": config["SUPABASE_URL"] or "",
    "MODEL_CLIENT_URL": config["MODEL_CLIENT_URL"] or "",
}