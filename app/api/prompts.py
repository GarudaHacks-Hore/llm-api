from app.libs.supabase import supabase

def get_prompts_from_room(room_id: str):
    response = supabase.table("prompts").select("chat, role").eq("roomId", room_id).execute()
    return response.data

def create_prompts(room_id: str, prompts: list):
    values = [{"roomId": room_id, "chat": p["content"], "role": p["role"]} for p in prompts]

    # values = [{"roomId": room_id, "chat": p.content, "role": p.role} for p in prompts]
    print(values)
    response = supabase.table("prompts").insert(values).execute()
    return response.data