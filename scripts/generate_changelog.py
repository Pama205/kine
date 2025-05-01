# scripts/generate_changelog.py
from git_changelog.build import Changelog
from git_changelog.templates import MarkdownTemplate

def generate_changelog():
    """Genera un archivo CHANGELOG.md siguiendo el estándar Keep a Changelog."""
    # Configuración principal
    changelog = Changelog(
        repository=".",  # Directorio del repositorio actual
        convention="angular",  # Convención de commits (angular, conventional, etc.)
        include_merge=False,  # Excluir commits de merge
        parse_refs=False,  # Mejor compatibilidad con Windows
    )

    # Configuración del template Markdown
    template = MarkdownTemplate(
        changelog=changelog,
        sections=["feat", "fix", "docs", "style", "refactor", "perf", "test"],
        section_titles={
            "feat": "🚀 Nuevas Funcionalidades",
            "fix": "🐛 Correcciones",
            "docs": "📚 Documentación",
            "style": "🎨 Estilo",
            "refactor": "♻️ Refactorizaciones",
            "perf": "⚡ Rendimiento",
            "test": "🧪 Pruebas"
        },
        show_author=False,  # Ocultar autores individuales
        show_issue=True,   # Mostrar referencias a issues
    )

    # Generar contenido
    content = template.render()

    # Escribir archivo
    with open("CHANGELOG.md", "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    generate_changelog()