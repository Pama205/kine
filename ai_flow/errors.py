# ai_flow/errors.py
class AIFlowError(Exception):
    """Base para todos los errores de la librería."""
    pass

class ProviderNotFoundError(AIFlowError):
    """Excepción cuando un proveedor no existe."""
    pass

class APIKeyNotFoundError(AIFlowError):
    """Excepción cuando falta una API key."""
    pass

class APIModelNotFoundError(AIFlowError):
    """Excepción cuando falta una API model."""
    pass