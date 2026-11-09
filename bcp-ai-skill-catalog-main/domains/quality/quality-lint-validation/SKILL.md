---
name: quality-lint-validation
description: Selecciona y ejecuta lint, typecheck y pruebas segun el stack del repositorio.
---

# Quality Lint Validation Skill

## Proposito
Convertir las validaciones tecnicas del squad en un resultado reproducible y seguro.

## Flujo
1. Detecta `package.json`, `pom.xml`, `build.gradle`, `pyproject.toml` u otros archivos de build.
2. Lee scripts existentes antes de ejecutar comandos.
3. Selecciona lint, typecheck y tests autorizados por el issue.
4. Clasifica el resultado como passed, code_failure, environment_missing o not_applicable.
5. Guarda evidencia redactada.

## Comandos permitidos
- Node: `npm run lint`, `npm test`, `npm run build`; alternativas `yarn`, `pnpm`.
- Java: `mvn test`, `./mvnw test`, `gradle test`, `./gradlew test`.
- Python: `python -m pytest`, `ruff check`, `mypy` si estan configurados.

## Reglas
- No instalar dependencias ni modificar lockfiles sin autorizacion.
- No desplegar.
- No ocultar fallos ni declarar passed si una prueba falla.
- Redactar variables, tokens y rutas sensibles.

## Adaptacion del squad
Reemplaza los comandos por los scripts oficiales del repositorio y documenta versiones de runtime.
