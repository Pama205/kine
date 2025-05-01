# examples/test_gemini.py
from ai_flow import AIFlow
from ai_flow.schemas.requests import TextGenerationRequest
from dotenv import load_dotenv
import os

load_dotenv()

api_key=os.getenv("GEMINI_API_KEY")
api_model="gemini-1.5-pro-latest"
# Inicialización
ai = AIFlow( "gemini", api_key, api_model )

# Solicitud estructurada
request = TextGenerationRequest(
    prompt="Explica la teoría de cuerdas en una frase",
    temperature=0.5,
    max_tokens=100
)
response = ai.generate_text(request)
print("Respuesta avanzada:", response.text)