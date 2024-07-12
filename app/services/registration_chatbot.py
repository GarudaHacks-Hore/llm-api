from openai import OpenAI
from torch import Tensor

def registration_chatbot(client: OpenAI, conversation_history: list, system_message: str, user_input: str | None, ollama_model: str = 'dolphin-llama3',):
    conversation_history.append({"role": "user", "content": user_input})

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

    return response