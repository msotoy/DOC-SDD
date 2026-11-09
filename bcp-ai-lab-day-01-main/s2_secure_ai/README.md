# S2 - Secure AI (discovery + review)

## Objetivo

Encontrar los hallazgos de seguridad en el código real y verificar que las correcciones estén bien hechas. Cubre los pasos 1 (discovery) y 3 (review).

## Contenido

- [`discovery.md`](discovery.md): prompt base para encontrar hallazgos.
- [`HALLAZGOS.md`](HALLAZGOS.md): plantilla vacía de la matriz (la genera `discovery.md` la primera vez).
- [`review.md`](review.md): prompt base de revisión con mirada de seguridad.

## Prompts por repo

Paso 1 (discovery): [`auth-backend`](../ejercicios/auth-backend/1-discovery.md) · [`frontend`](../ejercicios/frontend/1-discovery.md) · [`requirements-api`](../ejercicios/requirements-api/1-discovery.md)

Paso 3 (review): [`auth-backend`](../ejercicios/auth-backend/3-review.md) · [`frontend`](../ejercicios/frontend/3-review.md) · [`requirements-api`](../ejercicios/requirements-api/3-review.md)

## Produce

- `HALLAZGOS.md` en cada repo, con Id `H-xx` y al menos una fila "Pendiente" (entrada del Día 2).
