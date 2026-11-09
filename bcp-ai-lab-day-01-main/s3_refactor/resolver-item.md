# Plantilla — Resolver items de HALLAZGOS.md

Prompt genérico y reutilizable: sirve para cualquier item "Pendiente" de
`HALLAZGOS.md`, sin importar si llegó por discovery, por review, o porque lo
agregaste a mano. No es específico de refactor ni de seguridad. Es lo mismo
que hace `s3_refactor/refactor.md`, pero para todo lo que aparece **después**
del primer lote — no repitas ese prompt, usa este.

## Plantilla — Paso 1 (plan)

```text
CONTEXTO
HALLAZGOS.md tiene el backlog de items pendientes de este repositorio. Antes
de proponer cualquier cambio, consulta docs/ENDPOINTS.md y
docs/GOOD_PRACTICES.md.

OBJETIVO
Generar PLAN.md con la propuesta de corrección para [indica aquí los items:
uno, varios, o "los de mayor severidad"]. Un apartado por item.

RESTRICCIONES
No modifiques código todavía. No combines el alcance de dos items en un
mismo apartado.

FORMATO DE RESPUESTA
Un archivo PLAN.md con un apartado por item (## Item: <hallazgo>).
```

## Plantilla — Paso 2 (implementar y cerrar)

```text
CONTEXTO
PLAN.md ya fue aprobado. Úsalo como guía única.

OBJETIVO
Implementar cada item de PLAN.md, uno a la vez, con su prueba antes y
después. Actualizar su fila en HALLAZGOS.md antes de pasar al siguiente.

CRITERIOS DE ACEPTACION
Cada item queda con su propio diff y su propia prueba. Cada fila de
HALLAZGOS.md pasa a "Resuelto", con una nota corta de cómo se resolvió.

FORMATO DE RESPUESTA
Por cada item: el diff, la prueba en verde, y HALLAZGOS.md actualizado.
```

Ver el ejemplo real completo en [ejercicios/auth-backend/resolver-item.md](../ejercicios/auth-backend/resolver-item.md)
(y las versiones de los otros 2 repos, en esta misma carpeta).
