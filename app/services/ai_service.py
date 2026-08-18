import os

from dotenv import load_dotenv

from openai import OpenAI

from app.core.constants import (
    MOOD_PROMPTS,
    SYSTEM_PROMPT,
)


load_dotenv()

AI_API_KEY = os.getenv("AI_API_KEY")
AI_BASE_URL = os.getenv("AI_BASE_URL")
AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "llama3-8b-8192")

client = OpenAI(
    api_key=AI_API_KEY,
    base_url=AI_BASE_URL,
)


def rewrite_news_with_ai(original_text: str, mood: str) -> str:
    if mood not in MOOD_PROMPTS:
        raise ValueError("Неверное настроение")

    mood_instruction = MOOD_PROMPTS[mood]
    user_prompt = f"Инструкция по тону: {mood_instruction}\n\nИсходный текст новости:\n{original_text}"

    try:
        response = client.chat.completions.create(
            model=AI_MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Ошибка при обращении к AI API: {e}")
        return f"Не удалось переписать текст с помощью ИИ. Ошибка: {str(e)}"