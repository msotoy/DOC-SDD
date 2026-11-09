---
name: scaffold-microservice
description: Andamia un microservicio nuevo siguiendo los estándares del BCP (estructura de carpetas, configuración, health checks, observabilidad y tests base). Úsalo al iniciar un proyecto/servicio nuevo en Java/Spring Boot o Quarkus, cuando el usuario pida "crear un microservicio", "scaffolding", "nuevo servicio" o "arrancar un proyecto desde cero".
license: Propietario · NTT DATA / BCP
---

# Scaffold de microservicio (estándar BCP)

Eres responsable de generar el esqueleto de un microservicio nuevo conforme a los estándares del BCP. No improvises estructura: sigue exactamente las convenciones de abajo.

## Cuándo usar esta skill
Al crear un servicio desde cero. Si el proyecto ya existe, NO la uses (esto es scaffolding inicial, no modificación de código existente).

## Entradas (pregunta si faltan)
- `service_name`: nombre del servicio en kebab-case (ej. `pagos-notificaciones`).
- `stack`: `spring-boot` (default) o `quarkus`.
- `java_version`: `21` por defecto.
- `group_id`: por defecto `pe.com.bcp`.

## Flujo de trabajo
1. Confirma las entradas; aplica defaults si el usuario no las da.
2. Genera la estructura de carpetas estándar (ver más abajo).
3. Genera los archivos base: build (`pom.xml` o `build.gradle`), clase de arranque, configuración por entorno, endpoint de salud y un test de humo.
4. Incluye los componentes transversales obligatorios del BCP: health check, logging estructurado, configuración externalizada y un test base que compile.
5. Resume al final qué se generó y los siguientes pasos (no despliegues nada).

## Estructura estándar BCP
```
<service_name>/
├── src/main/java/pe/com/bcp/<service>/
│   ├── Application.java           # clase de arranque
│   ├── config/                    # configuración externalizada
│   ├── api/                       # controladores REST
│   ├── domain/                    # lógica de negocio
│   └── infra/                     # adaptadores (DB, mensajería)
├── src/main/resources/
│   ├── application.yml            # config base
│   └── application-{dev,prod}.yml # config por entorno
├── src/test/java/pe/com/bcp/<service>/
│   └── SmokeTest.java             # test base que debe compilar y pasar
├── pom.xml (o build.gradle)
└── README.md
```

## Estándares y reglas (obligatorias)
- **Health check**: expón `/health` (Spring Actuator o Quarkus Health). Debe responder el estado del servicio.
- **Logging estructurado**: JSON por defecto, sin `System.out.println`.
- **Configuración externalizada**: nada de secretos ni endpoints hardcodeados; todo vía `application-{env}.yml` o variables de entorno.
- **Java 21**, `group_id` = `pe.com.bcp` salvo indicación contraria.
- **Naming**: paquetes en minúscula; clases en PascalCase; el servicio en kebab-case.
- **Test base**: el `SmokeTest` debe verificar que el contexto arranca. No generes servicio sin al menos ese test.

## Salida esperada
- Árbol de archivos generado conforme a la estructura.
- Un README con: descripción, requisitos, cómo correr local y cómo correr los tests.
- Un resumen final con los siguientes pasos sugeridos (registrar el servicio en el catálogo, configurar CI, etc.). NO ejecutes despliegues.

## Qué NO hacer
- No añadir dependencias fuera de las necesarias para el esqueleto.
- No generar lógica de negocio real (es un andamiaje, no la implementación).
- No tocar proyectos existentes.
