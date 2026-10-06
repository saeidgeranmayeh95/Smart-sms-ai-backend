import json
import os
import re

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Smart SMS AI Backend")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    suggestions: list[str]


@app.get("/")
def root():
    return {"status": "ok", "service": "smart-sms-ai-backend"}


@app.get("/health")
def health():
    return {"status": "ok", "gemini_configured": bool(GEMINI_API_KEY)}


@app.post("/generate", response_model=GenerateResponse)
async def generate(data: GenerateRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not configured")

    prompt = (
        "You are a private SMS reply assistant. "
        "Return exactly 3 short, natural, friendly reply suggestions. "
        "Match the user's writing style when it is visible in the supplied context. "
        "Do not add explanations. Return only a JSON array of 3 strings.\n\n"
        + data.prompt
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "responseMimeType": "application/json"
        }
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            url,
            params={"key": GEMINI_API_KEY},
            json=payload,
        )

    if response.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"Gemini request failed ({response.status_code}): {response.text[:800]}")

    try:
        text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            parsed = parsed.get("suggestions", [])
        suggestions = [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        raw = response.text
        suggestions = [
            x.strip(" -0123456789.\t")
            for x in re.split(r"[\r\n]+", raw)
            if x.strip()
        ]

    if len(suggestions) < 3:
        raise HTTPException(status_code=502, detail="Gemini did not return 3 suggestions")

    return {"suggestions": suggestions[:3]}
