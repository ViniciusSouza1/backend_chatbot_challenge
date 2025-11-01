# src/app/services/embedder.py
import os
from typing import List
from openai import OpenAI

# Usa a OpenAI API. Certifique-se de ter OPENAI_API_KEY no seu ambiente.
client = OpenAI()

# Este modelo gera vetores de 1536 dimensões (alinha com seu Pinecone atual).
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Receive a list of vectors of size (1536-dim).
    """
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]