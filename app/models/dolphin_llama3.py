from app.libs.supabase import supabase
from app.utils.chunk_result import chunk_result
from app.configs.env import env
from openai import OpenAI
import ollama
import torch
import json

def generate_embedding():
    vault_content = get_vault_content_from_supabase("profiles")
    vault_embeddings = create_embedding_tensor(chunk_result(vault_content))
    vault_content = chunk_result(vault_content)
    # print(vault_content)
    return vault_embeddings, vault_content

def get_vault_content_from_supabase(table_name: str):
    # Get all rows from the table
    response = supabase.table(table_name).select("*").execute()
    data = response.data
    text = json.dumps(data, ensure_ascii=False)
    return text

def create_embedding_tensor(vault_content):
    print("Creating embedding tensor...")
    vault_embeddings = []
    for content in vault_content:
        response = ollama.embeddings(model='mxbai-embed-large', prompt=content)
        vault_embeddings.append(response["embedding"])

    # Convert to tensor and print embeddings
    vault_embeddings_tensor = torch.tensor(vault_embeddings) 
    return vault_embeddings_tensor

client = OpenAI(
    base_url=env["MODEL_CLIENT_URL"],
    api_key='dolphin-llama3'
)