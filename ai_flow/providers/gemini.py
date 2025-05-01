# ai_flow/providers/gemini.py
import google.generativeai as genai
from ..schemas.requests import TextGenerationRequest
from ..schemas.responses import TextGenerationResponse
from ..errors import APIKeyNotFoundError, APIModelNotFoundError
from dotenv import load_dotenv
import os

load_dotenv()

class GeminiProvider:
    """Implementación oficial del proveedor Google Gemini."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro-latest"):
        """Inicializa el cliente de Gemini.
        
        Args:
            api_key: Clave API de Google AI Studio
            model: Nombre del modelo a usar (por defecto: gemini-1.5-pro-latest)
        """
        if not api_key:
            raise APIKeyNotFoundError("Se requiere API key para Gemini")
            
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def generate_text(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """Genera texto usando el modelo Gemini.
        
        Args:
            request (TextGenerationRequest): Prompt y parámetros
            
        Returns:
            TextGenerationResponse: Respuesta estructurada
        """
        try:
            response = self.model.generate_content(
                contents=request.prompt,
                generation_config={
                    "temperature": request.temperature,
                    "max_output_tokens": request.max_tokens
                }
            )
            return TextGenerationResponse(
                text=response.text,
                model="gemini-pro"
            )
        except Exception as e:
            raise GeminiAPIError(f"Error en Gemini: {str(e)}")

class GeminiAPIError(Exception):
    """Error específico de la API de Gemini."""
    pass