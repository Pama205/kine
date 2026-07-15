# Changelog

## [0.1.0] - 2025-04-25

### Features
- Initial support for Google Gemini API
- Modular provider system (`gemini`, `openai`)
- Base `Kine` class with `generate_text()` method

### Bug Fixes
- Fixed initialization error with missing API keys
- Improved parameter validation in `TextGenerationRequest`

### BREAKING CHANGES
- Renamed `GeminiClient` to `GeminiProvider`
