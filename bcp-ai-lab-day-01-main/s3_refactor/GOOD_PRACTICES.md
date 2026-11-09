# Plantilla — docs/GOOD_PRACTICES.md

Se escribe **antes** del refactor, no después: el prompt `refactor.md` la
consulta para saber a qué converger.

## Plantilla

```
# Buenas prácticas — [nombre de tu proyecto]

> Convenciones a las que debe converger el refactor. Se consultan durante el
> refactor, no después.

- **Capas separadas**: [tu patrón de capas — ej. Controller/Service/Repository].
- **[Modelos/DTOs]**: [cómo separas entrada/salida de tus entidades internas].
- **[Dato sensible, ej. contraseñas]**: [cómo debe manejarse — hash, cifrado, nunca en logs].
- **[Autenticación/token]**: [esquema esperado — firmado, con expiración, etc.].
- **Configuración**: [variables de entorno / archivo de config], nunca secretos
  hardcodeados.
- **[Acceso a datos, ej. SQL]**: [siempre parametrizado / nunca concatenado].
- **Errores**: mensajes genéricos al cliente; el detalle completo solo en logs
  del servidor.
- **Dependencias**: si un scanner marca un CVE, se investiga y se corrige — no
  se silencia.
```

## Ejemplo real ([workshop-auth-backend/docs/GOOD_PRACTICES.md](https://github.com/NTTData-Academy/workshop-auth-backend-template/blob/instructor/docs/GOOD_PRACTICES.md))

```
# Buenas prácticas — Backend Quarkus

> Convenciones a las que debe converger el refactor de refactor.md. Se
> consultan durante el refactor, no después.

- Capas separadas: Resource (HTTP) → Service (reglas de negocio) →
  Repository (persistencia). Nada de lógica de negocio ni acceso a datos
  dentro del Resource.
- DTOs propios: la entidad de persistencia (UserRecord) no se devuelve tal
  cual en la respuesta HTTP; se mapea a un DTO de salida.
- Contraseñas: hash lento con salt (por ejemplo BCrypt). Nunca en texto
  plano, nunca en logs.
- Tokens: firmados, con expiración y claims explícitos.
- Configuración: variables de entorno o application.properties. Ningún
  secreto hardcodeado en una clase Java.
- SQL: siempre PreparedStatement o parámetros nombrados. Nunca concatenación
  de strings.
- Errores: mensajes genéricos al cliente. El detalle completo va solo al log
  del servidor.
- Dependencias: si CodeQL o Dependency Review marca un CVE, se investiga y
  se corrige — no se silencia.
```
