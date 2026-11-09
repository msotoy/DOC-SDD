# Plantilla — Prompt 03, Review

Contexto abierto a propósito: para este prompt, deja que quien revisa decida
qué documentos consultar (ya pasó el "primer contacto" con el repo).

## Plantilla

```text
CONTEXTO
El PR implementa uno o más hallazgos de HALLAZGOS.md. Consulta los
documentos del repositorio que consideres necesarios para justificar cada
observación (por ejemplo README.md, RETO.md, docs/ENDPOINTS.md,
docs/GOOD_PRACTICES.md, REGLAS.md) y al final dime cuáles usaste.

OBJETIVO
Revisar el PR verificando que cada hallazgo marcado "Resuelto" en
HALLAZGOS.md esté realmente corregido, buscando específicamente:
[tus categorías de riesgo típicas: inyección, autorización, validación,
excepciones verbosas, dependencias vulnerables, cobertura, duplicación].

RESTRICCIONES
No apruebes un PR que reduzca quality gates o que marque un hallazgo como
"Resuelto" sin corregirlo de verdad. No inventes riesgos que no puedas
señalar con archivo y línea.

CRITERIOS DE ACEPTACION
Cada hallazgo "Resuelto" queda verificado con evidencia, o vuelve a
"Pendiente" si el PR no lo corrigió del todo.

FORMATO DE RESPUESTA
Observaciones clasificadas en bloqueantes, importantes y sugerencias, con
evidencia para cada una. Si encuentras algo nuevo, agrégalo a HALLAZGOS.md
como fila "Pendiente" en vez de solo mencionarlo en el chat.
```

Ver el ejemplo real completo en [ejercicios/auth-backend/3-review.md](../ejercicios/auth-backend/3-review.md)
(y las versiones de los otros 2 repos, en esta misma carpeta).
