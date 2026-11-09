---
name: signed-token-security
description: Diseña o revisa tokens firmados con expiracion, claims minimos, secreto externalizado y evidencia.
---

# Signed Token Security Skill

## Proposito
Implementar o revisar un token de sesion sin romper el contrato del endpoint.

## Entradas requeridas
- Endpoint y response vigente.
- Claims requeridos: minimo `sub`, `client`, `iat`, `exp`.
- Duracion en segundos y tolerancia de reloj.
- Mecanismo autorizado: JWT/libreria o HMAC aprobado.
- Fuente de configuracion del secreto.

## Salidas
- Cambio de token o informe de gaps.
- Tests de claims, firma y expiracion.
- Configuracion documentada sin valores secretos.
- Evidencia redactada.

## Reglas
- Nunca hardcodear secretos reales.
- No imprimir tokens completos.
- No tratar el payload decodificado como prueba de autenticidad sin validar firma.
- Mantener status codes y campos compatibles salvo decision explicita.
- No incluir informacion sensible innecesaria en claims.

## Criterio de salida
`expiresIn` coincide con `exp`, el secreto proviene de configuracion y los tests demuestran contrato, expiracion y errores genericos.

## Adaptacion
El Tech Lead debe completar algoritmo, libreria, nombres de variables, claims de dominio y politica de rotacion.
