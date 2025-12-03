from app.models.openai_client import openai


def chat_completion(model: str, prompt: str, temperature: float = 0.2) -> str:
    resp = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return resp.choices[0].message.content
