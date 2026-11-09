---
name: credential-hashing-migration
description: Revisa y migra credenciales de laboratorio a hash lento con salt y seed reproducible.
---

# Credential Hashing Migration Skill

## Proposito
Eliminar contraseñas en texto plano sin perder las credenciales controladas del sandbox.

## Entradas
- Esquema y seed actual.
- Usuarios de laboratorio, nunca usuarios reales.
- Algoritmo aprobado y parametros.
- Estrategia de migracion y rollback.

## Flujo
1. Inspecciona columnas y seed sin mostrar valores sensibles.
2. Define algoritmo, salt, costo y formato almacenado.
3. Implementa seed idempotente o migracion controlada.
4. Prueba login valido, invalido y reinicio del entorno.
5. Verifica que logs y evidencia no contengan passwords, hashes completos o salts.

## Reglas
- No usar credenciales productivas.
- No registrar passwords ni material criptografico.
- No afirmar migracion completada sin inspeccion y tests.
- Documentar si la implementacion existente ya cumple el objetivo.

## Adaptacion
El Chapter Lead debe configurar el algoritmo aprobado, costo, formato de tabla y estrategia de seed para cada tecnologia.
