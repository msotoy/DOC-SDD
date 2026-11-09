---
name: safe-ui-messages
description: Elimina HTML dinamico inseguro y normaliza mensajes de error del frontend.
---

# Safe UI Messages Skill

## Proposito
Mostrar mensajes de validacion y error como texto seguro, consistente y util para el usuario.

## Flujo
1. Localiza `[innerHTML]`, `innerHTML`, templates dinamicos y mensajes provenientes del backend.
2. Cambia a interpolacion o binding de texto.
3. Mapea status codes y errores tecnicos a mensajes genericos.
4. Conserva detalles tecnicos solo en logging aprobado y redactado.
5. Agrega tests para mensaje, estado y error.

## Reglas
- No interpolar HTML proveniente de usuario o backend.
- No exponer stack traces, SQL, usernames sensibles ni tokens.
- No resolver el problema deshabilitando sanitizacion global.
- Mantener accesibilidad y comportamiento visual del flujo.

## Adaptacion
Definir en el squad catalogo de mensajes, idioma, severidades, componentes de notificacion y framework de testing.
