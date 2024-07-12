from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.models.dolphin_llama3 import client, generate_embedding
from app.services.user_chatbot import find_user_chatbot
from app.services.registration_chatbot import registration_chatbot
from app.services.summarize import summarize_text
from app.api.prompts import get_prompts_from_room, create_prompts
class UserPrompt(BaseModel):
    prompt: str
    identifier: str | None = None

class RegistrationPrompt(BaseModel):
    prompt: str
    phase: int
    conversation_history: list | None = None

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    r=create_prompts(prompt.identifier, new_conversation)

    return {"prompt": prompt.prompt, "answer": response.choices[0].message.content, "response": r}

@app.post("/summarize")
def create_summary(prompt: UserPrompt):
    response = summarize_text(client, prompt.prompt)
    return {"prompt": prompt.prompt, "answer": response.choices[0].message.content}

@app.post("/registration")
def register(prompt: RegistrationPrompt):

    conversation_history = prompt.conversation_history or []

    if (prompt.phase == 1):
        system_message = """
            Greet the new user and show some interest in their city and/or country.
            - Avoid introducing new topics or queries that deviate from the original query.
            - You must ask about what the user has been doing lately, what their current project is, or what their current most interesting thing is.
            Original query: [{prompt.prompt}]
            Answer query: 
        """

        response = client.chat.completions.create(
        model="dolphin-llama3",
        messages=[
            {"role": "system", "content": "You should only answer the question as stated. Do not add more text than necessary. Just output the name. You should also do the same for every language."},
            {"role": "user", "content": f"Get the user's name from the following text\n\nUSER TEXT:{prompt.prompt}\n\n"}
        ])
        summary = response.choices[0].message.content
    elif (prompt.phase == 2):
        system_message = """
            Be excited and say that their project is interesting. Ask the user what are the milestone's they have reached so far.
            It can be number of users or the development phase they are in.
            - Avoid introducing new topics or queries that deviate from the original query.
            - Ask for more details about their project. A sentence or two is sufficient, as long as the user's excitement is conveyed.
            Original query: [{prompt.prompt}]
            Answer query: 
        """
        summary = ""
    elif (prompt.phase == 3):
        system_message = """
            Be excited and say that their profile is all set up.
            - Avoid introducing new topics or queries that deviate from the original query.
            Original query: [{prompt.prompt}]
            Answer query:  
        """
        summary = ""


    response = registration_chatbot(client, conversation_history, system_message, prompt.prompt)

    return {"prompt": prompt.prompt, "answer": response.choices[0].message.content, "history": conversation_history, "summary": summary}