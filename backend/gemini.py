import os
from google import genai
from google.genai import types
from pydantic import BaseModel
from typing import Type, Optional

class GeminiClient:
    def __init__(self):
        # The Client automatically picks up GEMINI_API_KEY from environment variables
        self.client = genai.Client()
        self.model = "gemini-2.5-flash"

    def call_flash(self, prompt: str, system_instruction: str = None, response_schema: Optional[Type[BaseModel]] = None) -> str:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2
        )
        
        if response_schema:
            config.response_mime_type = "application/json"
            config.response_schema = response_schema

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=config
        )
        return response.text

gemini_client = GeminiClient()