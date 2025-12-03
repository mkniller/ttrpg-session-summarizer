from typing import List
import tiktoken
from app.config import MODEL_ANALYTICAL, MAX_CHUNK_TOKENS


def _get_encoder(model: str):
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str, model: str = MODEL_ANALYTICAL) -> int:
    enc = _get_encoder(model)
    return len(enc.encode(text))


def chunk_text(text: str, max_tokens: int = MAX_CHUNK_TOKENS, model: str = MODEL_ANALYTICAL) -> List[str]:
    enc = _get_encoder(model)
    tokens = enc.encode(text)
    chunks = []

    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = enc.decode(chunk_tokens)
        chunks.append(chunk_text)

    return chunks
