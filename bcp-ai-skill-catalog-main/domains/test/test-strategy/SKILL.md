---
name: test-strategy
description: Convierte requisitos y criterios de aceptacion en una estrategia de pruebas ejecutable y trazable.
---

# Test Strategy Skill

## Proposito
Definir que probar, en que nivel, con que datos y que evidencia demuestra el resultado.

## Entradas
- Historia de usuario y criterios de aceptacion.
- Contrato API y dependencias.
- Arquitectura y riesgos.
- Stack y herramientas de testing.
- Restricciones de ambiente y datos.

## Salidas
- Matriz requisito -> escenario -> prueba -> evidencia.
- Casos happy path, negativos, limites y errores.
- Niveles unit, integration, contract, component, E2E y security.
- Datos anonimizados y estrategia de fixtures.
- Comandos de ejecucion y umbral de cobertura.
- Gaps y riesgos residuales.

## Flujo
1. Identifica comportamiento y riesgo.
2. Selecciona nivel minimo de prueba.
3. Define casos medibles y datos seguros.
4. Relaciona cada caso con evidencia.
5. Ejecuta pruebas autorizadas y clasifica fallos.

## Reglas
- No afirmar cobertura sin ejecutar o adjuntar evidencia.
- No usar datos productivos.
- No probar ataques destructivos.
- La cobertura no sustituye casos funcionales ni de seguridad.
- Adaptar el umbral al repositorio, documentando excepciones.
