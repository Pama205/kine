# ai_flow/core.py
from typing import Dict, Type
from .errors import ProviderNotFoundError, APIKeyNotFoundError
from .schemas.requests import TextGenerationRequest
from .schemas.responses import TextGenerationResponse
import os

class AIFlow:
    """Punto de entrada principal para interactuar con proveedores de IA."""
    
    PROVIDERS = {
        'gemini': ('ai_flow.providers.gemini', 'GeminiProvider')
    }
    
    def __init__(self, provider: str = "gemini", api_key: str = None, model: str = None, **kwargs):
        """
        Args:
            provider: Nombre del proveedor ('gemini', 'openai', etc.)
            api_key: Clave API (opcional, puede estar en .env)
            model: Modelo específico a usar (opcional)
            **kwargs: Configuración adicional para el proveedor
        """
        self.provider = self._load_provider(provider, {
            'api_key': api_key,
            'model': model,
            **kwargs
        })

    def _load_provider(self, provider_name: str, config: Dict) -> Type:
        try:
            print(provider_name)
            if provider_name not in self.PROVIDERS:
                raise ProviderNotFoundError(f"Proveedor '{provider_name}' no existe")
            
            # Pasa la API key desde config o .env
            api_key = config.get('api_key') or os.getenv(f"{provider_name.upper()}_API_KEY")
            if not api_key:
                raise APIKeyNotFoundError(f"API key no proporcionada para {provider_name}")
            
            module_path, class_name = self.PROVIDERS[provider_name]
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)(**config)
        
        except (ImportError, AttributeError) as e:
            raise ProviderNotFoundError(
                f"Clase '{class_name}' no encontrada en módulo. "
                f"¿La clase está bien escrita en el archivo del proveedor?"
            ) from e

    def generate_text(self, prompt: str | TextGenerationRequest, **kwargs) -> TextGenerationResponse:
        """Genera texto usando el proveedor configurado.
        
        Args:
            prompt: Puede ser un string o un objeto TextGenerationRequest
            **kwargs: Parámetros adicionales (solo si prompt es string)
        """
        if isinstance(prompt, TextGenerationRequest):
            # Si ya es una Request, úsala directamente
            return self.provider.generate_text(prompt)
        else:
            # Si es string, crea una nueva Request
            request = TextGenerationRequest(prompt=prompt, **kwargs)
            return self.provider.generate_text(request)