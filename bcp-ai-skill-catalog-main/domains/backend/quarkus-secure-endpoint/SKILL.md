---
name: quarkus-secure-endpoint
description: 'Usa esta skill cuando el agente deba crear o modificar un endpoint REST en un proyecto Quarkus (Java), para que siga los estándares de autenticación, validación de entrada y manejo de errores del equipo.'
---

## Propósito
Estandarizar cómo se crean endpoints REST en Quarkus dentro de la
organización: autenticación, validación de entrada y manejo de errores
consistentes.

## Entradas
- Especificación funcional del endpoint (recurso, verbo HTTP, payload esperado).
- Contexto del proyecto: versión de Quarkus, mecanismo de auth ya presente
  (JWT, OIDC, etc.).

## Salidas
- Clase de recurso JAX-RS (`@Path`) con anotaciones de seguridad
  (`@RolesAllowed` o equivalente) aplicadas por defecto.
- Validación de entrada con Bean Validation (`@Valid`, `@NotNull`, etc.).
- Manejo de errores centralizado con `ExceptionMapper`, sin exponer stack
  traces ni detalles internos en la respuesta.

## Flujo
1. Confirmar el mecanismo de autenticación ya usado en el proyecto antes de
   proponer uno nuevo.
2. Generar el recurso JAX-RS con anotaciones de seguridad explícitas — nunca
   un endpoint sin control de acceso salvo que el usuario lo pida
   explícitamente y justifique por qué.
3. Añadir validación de entrada en el DTO/record del payload.
4. Mapear errores esperados a códigos HTTP apropiados vía `ExceptionMapper`,
   sin filtrar información sensible en el body de error.
5. Sugerir el test de integración correspondiente (`@QuarkusTest`).

## Constraints
- Nunca generar un endpoint público sin anotación de seguridad explícita sin
  advertir al usuario.
- No loguear el payload completo de requests que puedan contener PII o datos
  sensibles.

## Adaptación
- Si el repo usa SQLite/H2 en desarrollo y otro motor en producción,
  mantener las queries agnósticas al motor.
- Ajustar el esquema de roles (`@RolesAllowed`) a los roles reales definidos
  en el proyecto.
