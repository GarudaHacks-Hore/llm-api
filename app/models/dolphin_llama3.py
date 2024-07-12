from app.libs.supabase import supabase
from app.utils.chunk_result import chunk_result
from openai import OpenAI
import ollama
import torch
import json

def generate_embedding():
    vault_content = get_vault_content_from_supabase("profiles")
    vault_embeddings = create_embedding_tensor(chunk_result(vault_content))
    return vault_embeddings, vault_content

def get_vault_content_from_supabase(table_name: str):
    # Get all rows from the table
    response = supabase.table(table_name).select("*").execute()
    data = response.data
    tuples = [tuple(profile.values()) for profile in data]
    text = '\n'.join([str(tup) for tup in tuples])
    return text

def get_relevant_context(rewritten_input, vault_embeddings, vault_content, top_k=3):
    if vault_embeddings.nelement() == 0:  # Check if the tensor has any elements
        return []
    # Encode the rewritten input
    input_embedding = ollama.embeddings(model='mxbai-embed-large', prompt=rewritten_input)["embedding"]
    # Compute cosine similarity between the input and vault embeddings
    cos_scores = torch.cosine_similarity(torch.tensor(input_embedding).unsqueeze(0), vault_embeddings)
    # Adjust top_k if it's greater than the number of available scores
    top_k = min(top_k, len(cos_scores))
    # Sort the scores and get the top-k indices
    top_indices = torch.topk(cos_scores, k=top_k)[1].tolist()
    # Get the corresponding context from the vault
    relevant_context = [vault_content[idx].strip() for idx in top_indices]
    return relevant_context

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
    base_url='http://localhost:11434/v1',
    api_key='dolphin-llama3'
)