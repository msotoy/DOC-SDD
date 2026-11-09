# Prompt 02 — Refactor incremental

Resuelve **cualquier tipo** de hallazgo (Vulnerabilidad, Bug, Refactor o
Sugerencia) — el nombre "refactor" es por la actividad de esta sesión
(corregir código), no filtra por la columna "Tipo" de `HALLAZGOS.md`.

Este prompt es para el **primer lote**: los hallazgos que salieron de
`1-discovery.md`, apenas terminas de encontrarlos. Para cualquier hallazgo
que aparezca después (uno que quedó pendiente, uno nuevo de `3-review.md`,
uno que encontraste tú), usa [`resolver-item.md`](resolver-item.md) en vez de
repetir este — mismo mecanismo, sin volver a explicar todo el contexto.

Ejecuta esto para resolver los hallazgos marcados "Pendiente" en `HALLAZGOS.md`.
Tú eliges el alcance: puedes priorizar los **2 o 3 de mayor severidad** si el
tiempo apremia (no hace falta resolver los 6 de `RETO.md` en la sesión —
priorizar también es parte de lo que se practica), o resolverlos **todos** si
te alcanza. Va en dos pasos: primero el plan, después la implementación. No
saltes el paso 1.

## Paso 1 — Generar el plan (no tocar código)

```text
AMBITO
Trabaja unicamente en la carpeta workshop-login-frontend/ de reqflow-workspace.
Todas las rutas de este prompt son relativas a esa carpeta. No leas ni
modifiques los otros repositorios del workspace.

Analiza este código antes de modificarlo.

CONTEXTO
Consulta primero:
- docs/ENDPOINTS.md: flujo y contratos a preservar
- docs/GOOD_PRACTICES.md: convenciones a las que debe converger el codigo
- REGLAS.md: reglas del laboratorio
- HALLAZGOS.md: hallazgos confirmados con su estado

OBJETIVO
Tomar de HALLAZGOS.md estos hallazgos marcados "Pendiente":
[completa aquí cuáles vas a resolver ahora — los 2 o 3 de mayor severidad,
o todos si el tiempo te alcanza] y generar PLAN.md con la propuesta de
correccion para cada uno.

RESTRICCIONES
No cambies los contratos HTTP de docs/ENDPOINTS.md. No agregues dependencias
nuevas sin justificar. No asumas convenciones que no esten en
docs/GOOD_PRACTICES.md. No modifiques codigo todavia.

CRITERIOS DE ACEPTACION
PLAN.md tiene un apartado por hallazgo, con: que hallazgo de HALLAZGOS.md es,
el problema, el cambio propuesto (separacion de responsabilidades, tipado
estricto, manejo consistente de errores, o una alternativa acotada al token en
localStorage/al uso de [innerHTML], segun corresponda), los archivos a tocar,
y la prueba de caracterizacion a escribir antes de tocarlos. El contrato de
docs/ENDPOINTS.md se mantiene intacto. El cambio propuesto tambien respeta
las reglas de Clean Code de REGLAS.md (una responsabilidad por componente,
sin duplicacion, sin anidamiento profundo, sin valores magicos).

FORMATO DE RESPUESTA
Un archivo PLAN.md con esa estructura. No modifiques codigo todavia.
```

## Paso 2 — Implementar el plan aprobado

```text
AMBITO
Trabaja unicamente en la carpeta workshop-login-frontend/ de reqflow-workspace.
Todas las rutas de este prompt son relativas a esa carpeta. No leas ni
modifiques los otros repositorios del workspace.

Ya leiste PLAN.md. Úsalo como guia.

CONTEXTO
PLAN.md fue aprobado. docs/GOOD_PRACTICES.md sigue siendo la referencia de
como debe quedar el codigo.

OBJETIVO
Implementar unicamente lo que dice PLAN.md, hallazgo por hallazgo: la prueba de
caracterizacion primero, despues el cambio.

RESTRICCIONES
No apruebes cambios que muevan secretos al frontend. No agregues cambios fuera
de PLAN.md.

CRITERIOS DE ACEPTACION
El flujo funcional de docs/ENDPOINTS.md sigue funcionando igual (login, ver
tareas, cerrar sesion). Cobertura del codigo modificado en 85% o superior
(REGLAS.md). El codigo resultante respeta las reglas de Clean Code de
REGLAS.md, no solo el hallazgo puntual. Cada hallazgo resuelto queda marcado
"Resuelto" en HALLAZGOS.md, con una nota corta de como se resolvio.

FORMATO DE RESPUESTA
Por cada hallazgo: el diff conceptual, la prueba corriendo en verde antes y
despues, y HALLAZGOS.md actualizado. Al finalizar, explica cualquier
desviacion del plan y los riesgos residuales si quedan.
```

Si `HALLAZGOS.md` tiene más hallazgos "Pendiente" que quieras resolver después
de estos, o algo que surgió recién (un bug, una sugerencia de review), usa
[resolver-item.md](resolver-item.md) — mismo mecanismo, para un item a la vez o
varios, sin necesidad de repetir todo este prompt.
