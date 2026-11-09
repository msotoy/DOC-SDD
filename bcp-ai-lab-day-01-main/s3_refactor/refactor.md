# Plantilla — Prompt 02, Refactor

Resuelve **cualquier tipo** de hallazgo (Vulnerabilidad, Bug, Refactor o
Sugerencia) — el nombre "refactor" es por la actividad de esta sesión
(corregir código), no filtra por la columna "Tipo" de `HALLAZGOS.md`.

Úsalo para el **primer lote**: los hallazgos que salen del discovery inicial.
Para cualquier hallazgo que aparezca después (de un review, o encontrado a
mano), usa `resolver-item.md` en vez de repetir este.

No pidas "optimiza este código". Va en dos pasos: primero el plan, después la
implementación. No saltes el paso 1. Tú eliges el alcance: 2-3 hallazgos de
mayor severidad si el tiempo apremia, o todos si te alcanza.

## Plantilla — Paso 1 (generar el plan, no tocar código)

```text
Analiza este código antes de modificarlo.

CONTEXTO
Consulta primero:
- docs/ENDPOINTS.md: contrato a preservar
- docs/GOOD_PRACTICES.md: convenciones a las que debe converger el código
- REGLAS.md: reglas del laboratorio
- HALLAZGOS.md: hallazgos confirmados con su estado

OBJETIVO
Tomar los hallazgos marcados "Pendiente" en HALLAZGOS.md que decidas resolver
ahora (los 2 o 3 de mayor severidad, o todos si el tiempo alcanza) y generar
PLAN.md con la propuesta de corrección para cada uno.

RESTRICCIONES
No cambies el contrato de docs/ENDPOINTS.md. No agregues dependencias sin
justificar. No modifiques código todavía.

CRITERIOS DE ACEPTACION
PLAN.md tiene un apartado por hallazgo: qué hallazgo es, el problema, el
cambio propuesto ([tus técnicas de corrección típicas, ej: parametrizar SQL,
tipar, separar capas]), los archivos a tocar, y la prueba de caracterización
a escribir antes de tocarlos. El cambio propuesto también respeta las reglas
de Clean Code de REGLAS.md (una responsabilidad por función, sin
duplicación, sin anidamiento profundo, sin valores mágicos).

FORMATO DE RESPUESTA
Un archivo PLAN.md con esa estructura. No modifiques código todavía.
```

## Plantilla — Paso 2 (implementar el plan aprobado)

```text
Ya leíste PLAN.md. Úsalo como guía.

OBJETIVO
Implementar únicamente lo que dice PLAN.md, hallazgo por hallazgo: la prueba
de caracterización primero, después el cambio.

CRITERIOS DE ACEPTACION
El contrato de docs/ENDPOINTS.md sigue funcionando igual. Cobertura del
código modificado en [tu %] o superior. El código resultante respeta las
reglas de Clean Code de REGLAS.md, no solo el hallazgo puntual. Cada
hallazgo resuelto queda marcado "Resuelto" en HALLAZGOS.md, con una nota
corta de cómo se resolvió.

FORMATO DE RESPUESTA
Por cada hallazgo: el diff, el test en verde antes y después, y HALLAZGOS.md
actualizado.
```

Ver el ejemplo real completo en [ejercicios/auth-backend/2-refactor.md](../ejercicios/auth-backend/2-refactor.md)
(y las versiones de los otros 2 repos, en esta misma carpeta).
