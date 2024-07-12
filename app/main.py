from fastapi import FastAPI
from pydantic import BaseModel
from app.models.dolphin_llama3 import client

class UserPrompt(BaseModel):
    prompt: str

app = FastAPI()

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
    return {"message": "Generated prompt using llama3 model.", "prompt": prompt.prompt, "answer": response.choices[0].message.content}