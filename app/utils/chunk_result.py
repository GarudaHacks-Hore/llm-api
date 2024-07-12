import re

# result is in JSON
def chunk_result(input: str, chunk_size=1000) -> list[str]:
    # Normalize whitespace and clean up text
    text = re.sub(r'\s+', ' ', input).strip()
    
    # Split text into chunks by sentences, respecting a maximum chunk size
    sentences = re.split(r'(?<=[.!?]) +', text)  # split on spaces following sentence-ending punctuation
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        # Check if the current sentence plus the current chunk exceeds the limit
        if len(current_chunk) + len(sentence) + 1 < chunk_size:  # +1 for the space
            current_chunk += (sentence + " ").strip()
        else:
            # When the chunk exceeds 1000 characters, store it and start a new one
            chunks.append(current_chunk)
            current_chunk = sentence + " "
    if current_chunk:  # Don't forget the last chunk!
        chunks.append(current_chunk)
    return chunks