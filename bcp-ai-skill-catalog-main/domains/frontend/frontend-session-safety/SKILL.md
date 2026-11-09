---
name: frontend-session-safety
description: Extrae y prueba el manejo seguro de sesion, evitando persistencia innecesaria de tokens.
---

# Frontend Session Safety Skill

## Proposito
Mantener login, consumo de APIs y logout sin guardar tokens de sesion en `localStorage` por defecto.

## Flujo
1. Localiza login, dashboard, logout, guards y llamadas autenticadas.
2. Extrae sesion a un servicio.
3. Define memoria o `sessionStorage` con trade-off documentado.
4. Verifica redireccion sin sesion y limpieza en logout.
5. Ejecuta tests del servicio y del flujo.

## Reglas
- No guardar tokens en `localStorage` salvo excepcion aprobada.
- Separar preferencias no sensibles de credenciales.
- No imprimir tokens.
- Mantener contrato de API y comportamiento funcional.

## Adaptacion
El Chapter Lead debe definir framework, mecanismo de inyeccion, politica de recarga y cobertura minima.
