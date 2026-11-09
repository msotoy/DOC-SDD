---
name: security-review
description: Revisa cambios de seguridad, secretos, validacion, errores, sesiones y evidencia sin modificar codigo.
---

# Security Review Skill

## Proposito
Emitir una decision de seguridad trazable: approved, changes_requested o blocked.

## Flujo
1. Lee issue, alcance y archivos modificados.
2. Busca secretos, PII, logs sensibles y configuracion insegura.
3. Revisa autenticacion, autorizacion, validacion, errores y dependencias.
4. Comprueba tests y gaps.
5. Redacta findings con severidad, riesgo, recomendacion y evidencia.

## Reglas
- No explotar sistemas ni usar payloads destructivos.
- No imprimir secretos encontrados; redactar y detener la salida sensible.
- No aprobar por ausencia de evidencia.
- Separar hallazgo confirmado de hipótesis.

## Adaptacion
El Chapter Lead debe agregar controles del dominio: APIs, frontend, cloud, datos, mobile o mensajeria.
