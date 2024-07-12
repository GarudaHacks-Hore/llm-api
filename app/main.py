from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.models.dolphin_llama3 import client, generate_embedding
from app.services.user_chatbot import find_user_chatbot
from app.api.prompts import get_prompts_from_room, create_prompts
class UserPrompt(BaseModel):
    prompt: str
    identifier: str | None = None

app = FastAPI()
vault_embeddings, vault_content = generate_embedding()

@app.get("/")
def hello():
    return {"message": "API for LLM using llama3 model using custom database data. Made for GarudaHacks 5.0."}

@app.post("/generate")
def generate_prompt(prompt: UserPrompt):
    response = client.chat.completions.create(
        model="dolphin-llama3",
        messages=[
            {"role": "system", "content": "Answer as descriptively as possible."},
            {"role": "user", "content": prompt.prompt}
        ]
    )
    return {"prompt": prompt.prompt, "answer": response.choices[0].message.content}

@app.post("/regenerate-embeddings")
def regenerate_embeddings():
    global vault_embeddings, vault_content 
    vault_embeddings, vault_content = generate_embedding()
    return {"message": "Regenerated embeddings."}

@app.post("/find")
def find_users(prompt: UserPrompt):

    if not prompt.identifier:
        raise HTTPException(status_code=400, detail="Identifier not provided")

    past_histories = [{'content': item['chat'], 'role': item['role']} for item in get_prompts_from_room(prompt.identifier)]
    initial_system_prompt = "You are a helpful assistant that is an expert at extracting the most useful information from a given text. If you aren't confident on the answer with the given context or there is simply no data, you MUST say that you do not know. DO NOT MAKE UP THINGS THAT ARE NOT IN A USER'S DATA! Don't repeat the query just give straight, informative answers"

    response, new_conversation = find_user_chatbot(client, prompt.prompt, initial_system_prompt, vault_embeddings, vault_content, past_histories)

    create_prompts(prompt.identifier, new_conversation)

    return {"prompt": prompt.prompt, "answer": response.choices[0].message.content}