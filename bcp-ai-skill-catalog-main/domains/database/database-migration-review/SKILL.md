---
name: database-migration-review
description: Revisa migraciones de base de datos para compatibilidad, rollback, datos y seguridad.
---

# Database Migration Review Skill

## Proposito
Evitar migraciones incompatibles, destructivas o imposibles de revertir sin decision explicita.

## Entradas
- Migration files y schema actual.
- Modelo de datos y volumen aproximado no sensible.
- Version de la aplicacion.
- Reglas de deployment y rollback.
- Plan de backup o restore aprobado.

## Salidas
- Evaluacion de compatibilidad.
- Riesgos de lock, tiempo, datos y rollback.
- Orden de ejecucion y estrategia expand/contract.
- Pruebas sobre copia o entorno seguro.
- Decision y evidencia.

## Checklist
- Migration idempotente o controlada.
- Backward compatibility durante rollout.
- Indices y constraints revisados.
- Datos existentes preservados.
- Rollback o forward-fix documentado.
- No se exponen datos reales en logs.

## Reglas
- No ejecutar migraciones destructivas en produccion.
- No borrar o renombrar columnas sin plan aprobado.
- No incluir dumps con datos reales.
- No afirmar rollback si no fue probado o justificado.

## Adaptacion
El Chapter Lead configura Flyway, Liquibase, Prisma, Alembic, TypeORM u otra herramienta aprobada.
