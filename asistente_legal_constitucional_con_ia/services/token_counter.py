from typing import Dict, List

import tiktoken

MODEL_TO_ENCODING = {
    "gpt-4o": "o200k_base",
    "gpt-4o-mini": "o200k_base",
    "gpt-4.1": "o200k_base",
    "gpt-4.1-mini": "o200k_base",
    "gpt-4-turbo": "o200k_base",
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
}


def _get_encoding(model: str):
    name = MODEL_TO_ENCODING.get(model, "o200k_base")
    try:
        return tiktoken.get_encoding(name)
    except Exception:
        return tiktoken.get_encoding("cl100k_base")


def count_text_tokens(text: str, model: str) -> int:
    enc = _get_encoding(model)
    return len(enc.encode(text or ""))


def count_chat_tokens(messages: List[Dict[str, str]], model: str) -> int:
    enc = _get_encoding(model)
    tokens = 0
    per_message_overhead = 3
    for m in messages:
        tokens += per_message_overhead
        tokens += len(enc.encode(m.get("role", "")))
        tokens += len(enc.encode(m.get("content", "")))
    tokens += 3
    return tokens
