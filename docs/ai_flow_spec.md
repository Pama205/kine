# Especificación Técnica: Librería `ai-flow`

## 📌 Objetivo
Crear una librería Python open-source que simplifique la integración de múltiples proveedores de IA (Gemini, DeepSeek, OpenAI, etc.) mediante una interfaz unificada con:
- Soporte para modelos de texto e embeddings
- Gestión automática de caché
- Tipado fuerte y validación de datos
- Facilidad de extensión para nuevos proveedores

## 🏗 Estructura del Proyecto
```plaintext
ai-flow/
├── ai_flow/
│   ├── __init__.py           # Exportación de API pública
│   ├── core.py               # Clase principal AIFlow
│   ├── providers/            # Implementaciones por proveedor
│   │   ├── __init__.py       # Registro de proveedores
│   │   ├── openai.py         
│   │   ├── gemini.py
│   │   └── deepseek.py       # [PENDIENTE]
│   ├── schemas/              # Esquemas de datos
│   │   ├── requests.py
│   │   └── responses.py
│   ├── utils/
│   │   ├── cache.py          # [PENDIENTE]
│   │   ├── logger.py         # [MEJORAR]
│   │   └── safety.py         # Filtros de contenido
│   └── errors.py             # Excepciones personalizadas
├── tests/
│   ├── unit/
│   │   ├── test_core.py
│   │   └── test_providers/
│   │       ├── test_gemini.py
│   │       └── test_deepseek.py # [PENDIENTE]
├── examples/
│   ├── basic_usage.py
│   └── web_integration/
│       └── fastapi_app.py
├── docs/
├── scripts/
└── pyproject.toml            # Configuración de Poetry