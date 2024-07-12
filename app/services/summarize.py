from openai import OpenAI

def summarize_text(client: OpenAI, text: str):
    response = client.chat.completions.create(
        model="dolphin-llama3",
        messages=[
            {"role": "system", "content": "Summarize the text to be relatively shorter than the original text but still retain all important information and contexts."},
            {"role": "user", "content": f"Summarize the text to be relatively shorter than the original text but still retain all important information and contexts.\n\nTEXT TO SUMMARIZE:{text}"}
        ]
    )
    return response