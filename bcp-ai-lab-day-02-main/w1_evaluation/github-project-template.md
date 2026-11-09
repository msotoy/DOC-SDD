# GitHub Project - W1

## Configuracion

Crear un Project privado para la ola de formacion y usar un issue por asistente. El texto del issue debe contener un unico requisito funcional, criterios de aceptacion y restricciones del sandbox.

## Issue template

```markdown
## Requirement ID
W1-{{ID}}

## Context
ReqFlow (Nuvexa Andina Digital). Backend Quarkus + SQLite y frontend Angular.

## Functional requirement
{{UNIQUE_REQUIREMENT}}

## Acceptance criteria
- [ ] {{CRITERION_1}}
- [ ] {{CRITERION_2}}
- [ ] Tests updated and executed
- [ ] Evidence pack linked in pull request

## Constraints
- Use only the attendee repository.
- Do not expose credentials or secrets.
- Preserve POST /auth/login unless this issue explicitly changes it.
```

## Flujo del trainer

1. Duplicar la issue para cada asistente y cambiar `Requirement ID` y el requisito.
2. Asignar una issue a un unico repositorio individual.
3. Revisar que el PR enlace issue, requisitos, tests, tool run y decision humana.
4. Registrar la puntuacion W1 y el resultado en el Project.