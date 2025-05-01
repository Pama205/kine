# Registro de Cambios

## [Versión 0.1.0] - 2025-04-25

### 🚀 Nuevas Funcionalidades
- Soporte inicial para Google Gemini API
- Sistema de proveedores modular (`gemini`, `openai`)
- Clase base `AIFlow` con método `generate_text()`

### 🐛 Correcciones
- Solucionado error de inicialización con API keys faltantes
- Validación mejorada de parámetros en `TextGenerationRequest`

### ⚠️ Cambios Importantes
- **BREAKING**: Renombrado `GeminiClient` a `GeminiProvider`