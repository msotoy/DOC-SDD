# Resolver items de HALLAZGOS.md (prompt reutilizable)

Este prompt no es específico de seguridad ni de refactor: sirve para
**cualquier item "Pendiente" de `HALLAZGOS.md`**, sin importar si llegó ahí por
el discovery inicial (`1-discovery.md`), por un code review
(`3-review.md`), o porque lo agregaste a mano al encontrar un bug o una
sugerencia. Es lo mismo que hace `2-refactor.md`, pero para todo lo que
aparece **después** de ese primer lote — no repitas `2-refactor.md`, usa este.

Puedes indicar **uno o varios items a la vez** (por ejemplo: "resuelve los items
2 y 4", "resuelve los 3 de mayor severidad", o "sigue con el resto de
HALLAZGOS.md"). Si no indicas ninguno, se toma el de mayor severidad. Aunque
resuelvas varios en la misma tanda, cada item mantiene su propio plan, su
propio diff y su propia prueba — no se mezclan entre sí, para no perder de
vista cuál corrección resuelve cuál hallazgo.

## Paso 1 — Generar el plan (no tocar código)

```text
AMBITO
Trabaja unicamente en la carpeta workshop-requirements-api/ de reqflow-workspace.
Todas las rutas de este prompt son relativas a esa carpeta. No leas ni
modifiques los otros repositorios del workspace.

CONTEXTO
HALLAZGOS.md tiene el backlog de items pendientes de este repositorio (pueden
ser hallazgos de seguridad, bugs, deuda técnica o sugerencias de review). Antes
de proponer cualquier cambio, consulta docs/ENDPOINTS.md (contrato a preservar)
y docs/GOOD_PRACTICES.md (convenciones a las que debe converger el código).

OBJETIVO
Generar PLAN.md con la propuesta de corrección para [indica aquí los items:
por ejemplo "los items 2 y 4 de HALLAZGOS.md", o "los 3 de mayor severidad"].
Un apartado por item, cada uno con su propio alcance.

RESTRICCIONES
No modifiques código todavía. No combines el alcance de dos items en un mismo
apartado, aunque los resuelvas en la misma tanda. No cambies un contrato de
docs/ENDPOINTS.md salvo que el item lo pida explícitamente.

CRITERIOS DE ACEPTACIÓN
Por cada item incluido, PLAN.md dice: qué item de HALLAZGOS.md es, el cambio
propuesto, los archivos que se van a tocar, y qué prueba hay que escribir antes
de tocarlos.

FORMATO DE RESPUESTA
Un archivo PLAN.md con un apartado por item (## Item: <hallazgo>). No
modifiques código todavía.
```

## Paso 2 — Implementar el plan y cerrar los items

```text
AMBITO
Trabaja unicamente en la carpeta workshop-requirements-api/ de reqflow-workspace.
Todas las rutas de este prompt son relativas a esa carpeta. No leas ni
modifiques los otros repositorios del workspace.

CONTEXTO
PLAN.md ya fue revisado y aprobado. Úsalo como guía única.

OBJETIVO
Implementar cada item de PLAN.md, uno a la vez y en el orden en que aparecen,
con su prueba antes y después. Después de cada uno, actualizar su fila en
HALLAZGOS.md antes de pasar al siguiente.

RESTRICCIONES
No implementes items que no estén en PLAN.md. No reduzcas quality gates. No
avances al siguiente item si el anterior no quedó con su prueba en verde.

CRITERIOS DE ACEPTACIÓN
Cada item de PLAN.md queda con su propio diff y su propia prueba. Cada fila
correspondiente en HALLAZGOS.md pasa a estado "Resuelto", con una nota corta
(1-2 líneas) de cómo se resolvió y qué test o PR lo respalda. Los contratos
existentes de docs/ENDPOINTS.md siguen funcionando, salvo que algún item pidiera
cambiarlos a propósito.

FORMATO DE RESPUESTA
Por cada item: el diff, la prueba corriendo en verde antes y después del
cambio, y la fila de HALLAZGOS.md actualizada con la nota de resolución.
```

Si `HALLAZGOS.md` todavía tiene items "Pendiente" que quieras resolver, vuelve a
ejecutar este mismo prompt indicando cuáles.
