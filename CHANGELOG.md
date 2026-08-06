# Changelog

All notable changes to D.AI.SY will be documented in this file.

---

## [0.1.0] - August 2026

### Added

- Initial FastAPI backend
- Root endpoint
- Health endpoint
- Chat endpoint
- Gemini 2.5 Flash Lite integration
- Service architecture
- Request/Response schemas
- Swagger API
- Environment variable loading
- Secure API key management
- Repository documentation
- Initial architecture documentation
- Product documentation
- Vision documentation

### Security

- Removed exposed API key from Git history
- Added .gitignore protection
- Added .env.example
- Regenerated Gemini API key
### Version 0.2.0 – Agent Foundation

#### Base Agent Interface

- Added `app/agents/base_agent.py`
- Introduced the abstract `BaseAgent` interface.
- Established a common asynchronous contract (`run`) for all future agents.
- Defined a required `name` property for agent identification.
- No runtime behavior changed in this milestone.
