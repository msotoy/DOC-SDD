---
name: api-contract-review
description: Revisa compatibilidad de endpoints, schemas, errores y cambios contractuales.
---

# API Contract Review Skill

## Proposito
Evitar que una implementacion rompa consumidores al cambiar endpoints, request, response o errores.

## Flujo
1. Identifica contrato vigente y consumidores.
2. Compara request, response, status codes, headers y errores.
3. Clasifica cambios compatibles, breaking o ambiguos.
4. Propone pruebas de contrato y versionamiento.
5. Registra decision humana cuando el contrato no este definido.

## Reglas
- No inferir campos faltantes.
- Mantener ejemplos sin credenciales reales.
- Validar el contrato con tests o schema disponible.
- Adaptar rutas, herramientas y formato al estandar del squad.
