---
name: parameterized-query-review
description: Revisa consultas de autenticacion y persistencia para evitar concatenacion de entradas.
---

# Parameterized Query Review Skill

## Proposito
Demostrar que las entradas se pasan como parametros y que el comportamiento funcional se conserva.

## Flujo
1. Localiza consultas relacionadas con la HU.
2. Detecta concatenacion o interpolacion de entradas.
3. Verifica PreparedStatement, placeholders o equivalente ORM.
4. Ejecuta pruebas validas, invalidas y de error.
5. Registra archivo, consulta revisada, resultado y gap sin datos sensibles.

## Reglas
- No incluir payloads de explotacion en la salida.
- No imprimir credenciales ni consultas con valores reales.
- No cambiar comportamiento fuera del alcance.
- Si ya esta corregido, producir evidencia de auditoria en lugar de cambios artificiales.

## Adaptacion
Cambiar los patrones a JDBC, JPA, TypeORM, Prisma, SQLAlchemy u ORM aprobado por el squad.
