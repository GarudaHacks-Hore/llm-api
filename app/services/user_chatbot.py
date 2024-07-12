import ollama
import torch
from torch import Tensor
from openai import OpenAI

def get_relevant_context(rewritten_input: str, vault_embeddings: Tensor, vault_content: str, top_k=3):
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

def find_user_chatbot(client: OpenAI, user_input: str, system_message: str, vault_embeddings: Tensor, vault_content: str, conversation_history, ollama_model: str = 'dolphin-llama3',):
    new_conversations = []
    
    # Get relevant context from the vault
    relevant_context = get_relevant_context(user_input, vault_embeddings, vault_content, top_k=3)
    if relevant_context:
        # Convert list to a single string with newlines between items
        context_str = "\n".join(relevant_context)
        # print("Context Pulled from Documents: \n\n" + context_str)
    else:
        print("No relevant context found.")

    user_input_with_context = user_input
    if relevant_context:
        user_input_with_context = context_str + "\n\n" + user_input

    conversation_history.append({"role": "user", "content": user_input_with_context})
    new_conversations.append({"role": "user", "content": user_input})

    messages = [
        {"role": "system", "content": system_message},
        *conversation_history
    ]

    # Send the completion request to the Ollama model
    response = client.chat.completions.create(
        model=ollama_model,
        messages=messages,
    )
    
    # Append the model's response to the conversation history
    conversation_history.append({"role": "assistant", "content": response.choices[0].message.content})
    new_conversations.append({"role": "assistant", "content": response.choices[0].message.content})
    
    # Return the content of the response from the model
    return response, new_conversations