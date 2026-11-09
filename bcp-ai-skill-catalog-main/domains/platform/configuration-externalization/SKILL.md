---
name: configuration-externalization
description: Detecta y corrige configuracion hardcodeada, separando defaults de laboratorio y secretos por entorno.
---

# Configuration Externalization Skill

## Proposito
Permitir que un repositorio se ejecute en local, CI y otros entornos sin editar codigo ni exponer secretos.

## Controles
- URLs, puertos, origins y nombres de servicios.
- Secretos y claves de firma.
- Configuracion frontend por entorno.
- Variables requeridas, defaults seguros y validacion al arranque.

## Flujo
1. Detecta valores hardcodeados.
2. Clasifica valor publico, secreto, default de sandbox o dato productivo.
3. Mueve configuracion a environment, properties o secret manager autorizado.
4. Documenta variables y ejemplos no sensibles.
5. Ejecuta pruebas con configuracion de test.

## Reglas
Nunca commitear secretos reales. Los defaults de laboratorio deben estar marcados como no productivos. Los componentes no deben conocer URLs directamente.
