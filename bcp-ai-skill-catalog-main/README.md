# skills-catalog

Catálogo central de **Agent Skills** de GitHub Copilot para la organización.
Cada skill vive en `domains/<dominio>/<skill>/SKILL.md` y sigue el formato
estándar de `agentskills.io` para que Copilot pueda cargarla cuando sea
relevante en Copilot CLI, cloud agent, code review y modo agente de VS Code.

El inventario publicado se mantiene en [`SKILLS-MANIFEST.json`](SKILLS-MANIFEST.json).
Actualmente contiene **32 skills**, agrupadas en **12 dominios**.

## Inventario de skills

La siguiente lista se genera a partir de `SKILLS-MANIFEST.json`:

| Dominio | Skill | Descripción | Estado |
| --- | --- | --- | --- |
| api | `api-contract-generation` | Genera contratos OpenAPI trazables desde historias de usuario y los valida con sus consumidores. | ok |
| architecture | `api-contract-review` | Revisa compatibilidad de endpoints, schemas, errores y cambios contractuales. | ok |
| architecture | `architecture-decision` | Evalúa impacto técnico y registra decisiones incrementales (brownfield) con estrategia y pruebas necesarias. | ok |
| architecture | `senior-architect` | Diseña arquitecturas escalables, ADRs, descomposición de servicios y patrones de integración. | ok |
| backend | `code-generation` | Genera módulos Java 21/Spring Boot completos. | ok |
| backend | `code-generation-henry` | Variante de `code-generation` para módulos Java 21/Spring Boot. | duplicate-of: `code-generation` |
| backend | `code-generator-nodejs` | Genera un backend NestJS 10 y TypeScript desde OpenAPI 3.0 o una implementation spec. | missing-frontmatter |
| backend | `scaffold-microservice` | Andamia microservicios Spring Boot o Quarkus con health check, observabilidad y tests base. | ok |
| backend | `quarkus-secure-endpoint` | Crea o modifica endpoints REST en Quarkus con autenticación, validación y manejo de errores. | ok |
| database | `database-migration-review` | Revisa migraciones por compatibilidad, rollback, datos y seguridad. | ok |
| frontend | `frontend-feature-generation` | Genera funcionalidades con componente, servicio, rutas, estados, accesibilidad y pruebas. | ok |
| frontend | `frontend-session-safety` | Extrae y prueba el manejo seguro de sesión, evitando persistencia innecesaria de tokens. | ok |
| frontend | `safe-ui-messages` | Elimina HTML dinámico inseguro y normaliza mensajes de error del frontend. | ok |
| frontend | `angular-accessible-form` | Crea o modifica formularios Angular con validación reactiva y mensajes accesibles. | ok |
| governance | `sdlc-documentation` | Mantiene documentación trazable de requisitos, decisiones, cambios, pruebas y evidencia. | ok |
| governance | `versioning-quality-gate` | Revisa versionado, changelog, commits, tags y trazabilidad. | ok |
| platform | `configuration-externalization` | Detecta configuración hardcodeada y separa defaults de laboratorio y secretos por entorno. | ok |
| quality | `quality-lint-validation` | Selecciona y ejecuta lint, typecheck y pruebas según el stack. | ok |
| quality | `discovery-analysis` | Investiga un sistema existente y produce hallazgos con evidencia sin modificar código. | ok |
| quality | `issue-implementation` | Implementa un issue aprobado de forma incremental, con pruebas, validaciones y PR auditable. | ok |
| review | `pull-request-review` | Revisa pull requests con checklist de contrato, seguridad, calidad, pruebas, documentación y versionamiento. | ok |
| review | `reqflow-definition-of-done` | Evalúa criterios transversales de ReqFlow: contratos, CI, seguridad, evidencia y PR auditable. | ok |
| security | `credential-hashing-migration` | Revisa y migra credenciales a hash lento con salt y seed reproducible. | ok |
| security | `dependency-review` | Revisa dependencias, CVEs, licencias, actualizaciones y evidencia de impacto. | ok |
| security | `parameterized-query-review` | Revisa consultas para evitar concatenación de entradas. | ok |
| security | `security-review` | Revisa seguridad, secretos, validación, errores, sesiones y evidencia sin modificar código. | ok |
| security | `signed-token-security` | Diseña o revisa tokens firmados con expiración, claims mínimos y secreto externalizado. | ok |
| security | `secure-secrets-handling` | Evita credenciales, tokens y secretos hardcodeados en código, configuración o CI/CD. | ok |
| specification | `grill-me-bcp` | Construye prompts con los cinco ejes BCP mediante una entrevista crítica, una pregunta por turno. | ok |
| specification | `spec-initial-definition` | Convierte historias y requisitos en una especificación técnica BDD completa. | ok |
| specification | `spec-writing` | Convierte un hallazgo o necesidad aprobada en una spec verificable, con alcance, contratos y criterios de aceptación. | ok |
| test | `test-strategy` | Convierte requisitos y criterios de aceptación en una estrategia de pruebas ejecutable y trazable. | ok |

Los estados distintos de `ok` reflejan el manifiesto actual y deben resolverse
antes de considerar esas skills plenamente listas para consumo.

## Uso mediante ISSUES

Los procesos operativos se solicitan desde las plantillas de ISSUE del
catálogo. Los repositorios destino pertenecen a la organización
`NTTData-Academy` y se indican separados por comas, sin incluir el owner.

### Onboarding de un repositorio

Crear un ISSUE con la plantilla **Onboarding de nuevo repositorio**, que aplica
el label `repo-onboarding`. El workflow `onboard-repo-on-issue.yml`:

1. Lee los repositorios y dominios seleccionados.
2. Copia `docs/consumer-workflow-template.yml` como
   `.github/workflows/sync-skills.yml` en la rama por defecto de cada repo.
3. Registra o actualiza el repo y sus dominios en `subscribers.json`.
4. Comenta el resultado en el ISSUE y lo cierra cuando termina correctamente.

También puede ejecutarse manualmente desde Actions con `workflow_dispatch`,
indicando `repos` y `domains`.

### Instalación o actualización de skills

Crear un ISSUE con la plantilla **Instalar / actualizar Skills en un repositorio**,
que aplica el label `skills-install`. El workflow
`install-skills-on-issue.yml`:

1. Lee los repositorios y skills marcados en el checklist.
2. Resuelve el dominio de cada skill mediante `SKILLS-MANIFEST.json`.
3. Si un repositorio no está suscrito, dispara automáticamente el onboarding.
4. Copia cada skill a `.github/skills/<skill>` desde su ruta en `domains/`.
5. Crea un commit por skill y hace push a la rama por defecto.
6. Actualiza los dominios del repositorio en `subscribers.json`, comenta el
   resultado y cierra el ISSUE.

## Workflows de automatización

| Workflow | Disparador | Función |
| --- | --- | --- |
| `onboard-repo-on-issue.yml` | ISSUE con `repo-onboarding` o ejecución manual | Configura el workflow consumidor y registra el repositorio. |
| `install-skills-on-issue.yml` | ISSUE con `skills-install` | Instala o actualiza skills y sus dominios registrados. |
| `validate-skills.yml` | PR o push a `main` con cambios en `domains/**` | Ejecuta `scripts/validate_skill.sh` y valida frontmatter, nombre y convención de carpetas. |
| `notify-subscribers.yml` | Push a `main` con cambios en `domains/**` | Envía `repository_dispatch` (`skills-catalog-updated`) a cada repo de `subscribers.json`. |

Cada repositorio consumidor usa `sync-skills.yml`, basado en
`docs/consumer-workflow-template.yml`. Responde al dispatch, permite ejecución
manual y tiene una sincronización semanal de respaldo. Hace checkout disperso
de los dominios configurados, actualiza `.github/skills/` y abre el PR
`chore/sync-skills-catalog` para revisión.

## Configuración y permisos

Los workflows que escriben en repositorios necesitan una GitHub App instalada
en los repos participantes de `NTTData-Academy`, con permisos `Contents: read
and write` y `Workflows: read and write`, y los secrets `APP_ID` y
`APP_PRIVATE_KEY` en el catálogo.

La notificación requiere `CATALOG_DISPATCH_TOKEN`, con permisos para ejecutar
`repository_dispatch` en los repos suscritos. Si el catálogo es privado, cada
consumidor necesita `CATALOG_READ_TOKEN` con permiso de lectura sobre este repo.

## Estructura

```text
skills-catalog/
├── domains/                         # skills agrupadas por dominio
├── template/SKILL.md.template       # plantilla para nuevas skills
├── scripts/validate_skill.sh        # validación local y de CI
├── docs/                            # onboarding y workflow consumidor
├── SKILLS-MANIFEST.json             # inventario y resolución skill -> dominio
├── subscribers.json                  # repos suscritos y dominios de interés
└── .github/
    ├── ISSUE_TEMPLATE/              # formularios de onboarding e instalación
    └── workflows/                   # automatizaciones del catálogo
```

## Agregar una skill

1. Copiar `template/SKILL.md.template` a
   `domains/<dominio>/<nombre-skill>/SKILL.md`.
2. Completar el frontmatter (`name` y `description`) y el cuerpo.
3. Actualizar `SKILLS-MANIFEST.json` con identificador, dominio, ruta,
   descripción y estado.
4. Abrir un PR. `validate-skills.yml` comprobará todas las skills bajo
   `domains/`.
5. Tras hacer merge a `main`, `notify-subscribers.yml` notificará a los repos
   suscritos.

## Convención de redacción

Además del frontmatter mínimo requerido por Copilot, cada `SKILL.md` debe
seguir la estructura auditable definida en la plantilla:

- **Propósito**
- **Entradas**
- **Salidas**
- **Flujo**
- **Constraints**
- **Adaptación**

## Suscripción manual

Para configurar un consumidor sin ISSUE, consultar
[`docs/SETUP-CONSUMER-REPO.md`](docs/SETUP-CONSUMER-REPO.md). El procedimiento
registra el repo, copia `sync-skills.yml`, configura los tokens necesarios y
ejecuta una primera sincronización.
