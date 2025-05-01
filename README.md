# AI Flow - Integración Unificada de Modelos de IA

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Poetry](https://img.shields.io/badge/packaging-poetry-cyan)

Una librería Python para integrar múltiples proveedores de IA (Gemini, OpenAI, etc.) con una interfaz simple y unificada.

## 🔥 Características Principales

- **Soporte multi-proveedor**: Gemini, OpenAI, DeepSeek y más
- **Interfaz unificada**: Mismos métodos para todos los proveedores
- **Tipado fuerte**: Validación automática de entradas/salidas
- **Fácil extensión**: Añade nuevos proveedores en minutos

## 📦 Instalación

```bash
# Instalar con Poetry (recomendado)
poetry add ai-flow --extras "all"

# O con pip
pip install ai-flow[all]
```

## 🏗 Estructura del Proyecto
```plaintext
ai-flow/
├── ai_flow/               # Paquete principal
│   ├── __init__.py        # Exporta clases/funciones principales
│   ├── core.py            # Clase `AIFlow` (punto de entrada)
│   ├── providers/         # Conexiones a APIs/modelos
│   │   ├── __init__.py
│   │   ├── openai.py      # Soporte para OpenAI
│   │   ├── huggingface.py # Soporte para HF Inference API
│   │   └── local.py       # Modelos ONNX/TensorFlow Lite
│   ├── models/            # Modelos pre-entrenados locales (opcional)
│   ├── utils/             # Helpers
│   │   ├── cache.py       # Caché con Redis/SQLite
│   │   └── ethics.py      # Filtros de contenido
├── tests/                 # Tests unitarios
│   ├── test_core.py
│   └── test_providers.py
├── examples/              # Ejemplos de uso
│   ├── basic_usage.py
│   └── web_integration.py
├── docs/                  # Documentación
│   ├── quickstart.md
│   └── api_reference.md
├── pyproject.toml         # Configuración de build (Poetry)
├── README.md              # Doc principal (badges, instalación)
└── LICENSE                # MIT/Apache 2.0
```

## 🚀 Uso Rápido

```bash
from ai_flow import AIFlow
from dotenv import load_dotenv

load_dotenv()  # Carga API keys desde .env

# Inicialización
ai = AIFlow(
    provider="gemini",  # También "openai", "deepseek"
    model="gemini-1.5-pro-latest"  # Modelo opcional
)

# Generación de texto
response = ai.generate_text(
    "Explica el quantum computing en una frase"
)
print(response.text)
```

## 🛠 Desarrollo

1- Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/ai-flow.git
cd ai-flow
```

2- Instala dependencias:
```bash
poetry install --extras "all"
```

3- Ejecuta tests:
```bash
poetry run pytest -v    
```

## 🤝 Contribución

¡Contribuciones son bienvenidas! Sigue estos pasos:

1- Abre un Issue para discutir el cambio

2- Haz fork del proyecto

3- Crea una rama con tu feature (git checkout -b feature/awesome-feature)

4- Haz commit de tus cambios (git commit -m 'Add awesome feature')

5- Haz push a la rama (git push origin feature/awesome-feature)

6- Abre un Pull Request

## 📜 Historial de Cambios
Consulta el [CHANGELOG.md](CHANGELOG.md) para detalles de cada versión.

## 📬 Contacto

- **Creador**: Pedro A. Martínez A.
- **Email**: pama205@gmail.com
- **GitHub**: [@pama205](https://github.com/pama205)