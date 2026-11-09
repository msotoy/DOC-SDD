# Plantilla — S1, Prompting + Context Engineering

El framework de 5 partes, genérico para cualquier proyecto. Copia este bloque
y completa cada sección — no la saltes aunque parezca lento, es lo que
convierte un pedido en algo que se puede revisar.

## Plantilla

```text
CONTEXTO
Qué existe ya (archivos, contrato, decisiones previas). En tu proyecto, según
lo que necesites, consulta: [tu archivo de reglas], [tu archivo de hallazgos],
[tu contrato de API], [tus buenas prácticas].

OBJETIVO
Qué quieres lograr, en una frase.

RESTRICCIONES
Qué no se puede romper: contratos, dependencias, comportamiento existente.

CRITERIOS DE ACEPTACION
Cómo se sabe que funciona. Tiene que ser verificable, no una opinión.

FORMATO DE RESPUESTA
Cómo quieres que responda la IA: plan primero, diff, tests corriendo, una
tabla, un archivo nuevo, etc.
```

## Qué suele cambiar según tu rol

- **Backend**: tu CONTEXTO parte del contrato de API y las convenciones de
  código. Tus CRITERIOS suelen incluir un código de estado HTTP y un test.
- **Frontend**: tu CONTEXTO necesita saber qué endpoint consumes y qué
  componente se ve afectado.
- **QA / Cyber**: tu CONTEXTO parte de la matriz de hallazgos, no del código
  en sí. Tus CRITERIOS casi siempre piden evidencia antes que una corrección.
- **Chapter / Líder Técnico**: tu OBJETIVO suele ser priorizar o coordinar,
  no programar directamente.

## Ejemplo real

Ver [ejercicios/auth-backend/template.md](../ejercicios/auth-backend/template.md) —
mismo framework, ya adaptado a ese proyecto en particular (y las versiones de
los otros 2 repos, en esta misma carpeta).
