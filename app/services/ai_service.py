from __future__ import annotations

import json

import httpx
from fastapi import HTTPException

from app.config import get_settings


class AIService:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def improve_content(self, action: str, content: str) -> str:
        if not self.settings.openai_api_key:
            raise HTTPException(
                status_code=503,
                detail="AI is unavailable. Please set OPENAI_API_KEY in your .env file.",
            )

        prompt = self._build_prompt(action, content)
        system_prompt = (
            "You improve resume content for ATS readability. "
            "Return concise professional text only, with no markdown."
        )
        return await self._chat_completion(system_prompt=system_prompt, user_prompt=prompt, temperature=0.6)

    async def check_ats_resume(self, resume_text: str, target_role: str) -> str:
        if not self.settings.openai_api_key:
            raise HTTPException(
                status_code=503,
                detail="AI is unavailable. Please set OPENAI_API_KEY in your .env file.",
            )

        system_prompt = (
            "You are an ATS resume auditor. Analyze resumes for keyword relevance, structure, readability, "
            "impact language, measurable outcomes, and formatting risks. Respond in plain text only."
        )
        user_prompt = (
            f"Target job role: {target_role or 'General role'}\n\n"
            "Review this resume text and return:\n"
            "1) ATS Score out of 100\n"
            "2) 5 strengths\n"
            "3) 8 improvements with exact rewrite guidance\n"
            "4) Missing keywords to add\n"
            "5) A 6-step action plan to improve interview chances\n\n"
            f"Resume text:\n{resume_text[:9000]}"
        )
        return await self._chat_completion(system_prompt=system_prompt, user_prompt=user_prompt, temperature=0.4)

    async def _chat_completion(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        payload = {
            "model": self.settings.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }

        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        endpoint = f"{self.settings.openai_base_url.rstrip('/')}/chat/completions"
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(endpoint, headers=headers, content=json.dumps(payload))
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as exc:
                raise HTTPException(status_code=502, detail=f"AI provider error: {exc.response.text}") from exc
            except httpx.HTTPError as exc:
                raise HTTPException(status_code=502, detail=f"AI connection error: {str(exc)}") from exc

        result = data["choices"][0]["message"]["content"].strip()
        if not result:
            raise HTTPException(status_code=502, detail="AI provider returned an empty response.")
        return result

    def _build_prompt(self, action: str, content: str) -> str:
        if action == "summary":
            return (
                "Rewrite this resume summary to sound ATS-friendly, clear, and results-oriented. "
                "Keep it under 90 words.\n\n"
                f"{content}"
            )
        return (
            "Rewrite these resume experience bullets for ATS readability. "
            "Use strong action verbs, measurable outcomes when possible, and keep each bullet concise.\n\n"
            f"{content}"
        )
