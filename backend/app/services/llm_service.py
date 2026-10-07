import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("dataproof.llm")

def call_gemini_api(prompt: str, json_schema: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Calls Gemini API using google-genai or direct HTTP requests.
    Returns raw text output from the model.
    """
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.info("No GEMINI_API_KEY found in environment. Using intelligent fallback agent.")
        return None

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=2048,
        )
        if json_schema:
            config.response_mime_type = "application/json"
            config.response_schema = json_schema

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )
        return response.text
    except Exception as e:
        logger.error(f"Error calling Gemini API SDK: {e}. Trying HTTP fallback.")
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.1}
            }
            if json_schema:
                payload["generationConfig"]["responseMimeType"] = "application/json"

            resp = requests.post(url, headers=headers, json=payload, timeout=15)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                logger.error(f"Gemini API HTTP returned error {resp.status_code}: {resp.text}")
        except Exception as http_err:
            logger.error(f"Gemini API HTTP fallback error: {http_err}")
    
    return None
