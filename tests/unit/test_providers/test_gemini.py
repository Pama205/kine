# examples/test_gemini.py
from ai_flow import AIFlow
from ai_flow.schemas.requests import TextGenerationRequest

ai = AIFlow("gemini")

# Opción 1: Usando string simple (crea Request automáticamente)
#response = ai.generate_text("Explica quantum computing")
#print(response.text)

# Opción 2: Usando Request explícita (NO anidada)
request = TextGenerationRequest(
    prompt="Traduce: Hello world",
    temperature=0.5
)
response = ai.generate_text(request)  # Pasa el objeto directamente
print(response.text)