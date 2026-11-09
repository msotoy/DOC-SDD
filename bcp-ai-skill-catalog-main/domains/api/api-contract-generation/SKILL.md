---
name: api-contract-generation
description: Genera contratos OpenAPI trazables desde historias de usuario y los valida con sus consumidores.
---

# API Contract Generation Skill

## Proposito
Convertir una historia de usuario o requisitos aprobados en un contrato API versionable, implementable y verificable.

## Entradas
- Historia de usuario y criterios de aceptacion.
- Consumidores conocidos.
- Recursos, operaciones y reglas de negocio.
- Requisitos de seguridad, errores y observabilidad.
- Version y formato aprobado: OpenAPI YAML/JSON u otro estandar del squad.

## Salidas
- Contrato OpenAPI completo.
- Schemas de request, response y errores.
- Status codes y headers.
- Ejemplos sin datos reales.
- Preguntas abiertas y decisiones de versionamiento.
- Pruebas o comandos de validacion del contrato.

## Flujo
1. Extrae recursos y operaciones sin inventar campos.
2. Define request, response, errores, autenticacion y paginacion cuando aplique.
3. Identifica compatibilidad con consumidores.
4. Genera ejemplos anonimizados.
5. Valida el documento y registra gaps.

## Reglas
- No inventar requisitos faltantes.
- No incluir secretos, tokens reales ni PII.
- Marcar cambios breaking.
- Mantener nombres, convenciones y version del squad.
- No generar implementacion si el contrato no esta aprobado.

## Adaptacion
El Tech Lead define versionado, formato, nomenclatura, herramienta de lint y politica de compatibilidad.

## Criterio de salida
El contrato puede ser revisado por API, backend, frontend y QA sin explicacion adicional.
