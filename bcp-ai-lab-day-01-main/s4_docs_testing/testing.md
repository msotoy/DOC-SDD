# Plantilla — Prompt 05, Testing

Ejecuta esto después de `endpoints.md`.

## Plantilla

```text
CONTEXTO
[Tu proyecto], ya refactorizado. docs/ENDPOINTS.md ya refleja el contrato
real. Consulta ese archivo, REGLAS.md (meta de cobertura) y cualquier otro
documento que consideres necesario.

OBJETIVO
Generar docs/TESTING.md y completar las pruebas que falten para cada
endpoint/función de docs/ENDPOINTS.md, cubriendo tres categorías: camino
feliz, casos borde y errores.

RESTRICCIONES
No inventes comportamientos que no estén en docs/ENDPOINTS.md. No adaptes un
test para que pase con un bug existente: si encuentras un bug, repórtalo
aparte, no lo escondas dentro del test.

CRITERIOS DE ACEPTACION
Por cada endpoint hay al menos: un test de camino feliz, un test de caso
borde, y un test por cada respuesta de error documentada. Cobertura del
código modificado en [tu %] o superior.

FORMATO DE RESPUESTA
El archivo docs/TESTING.md con una tabla (endpoint | caso | tipo | resultado
esperado) y después el código de los tests, corriendo en verde.
```

Ver el ejemplo real completo en [ejercicios/auth-backend/5-testing.md](../ejercicios/auth-backend/5-testing.md)
(y las versiones de los otros 2 repos, en esta misma carpeta).
El resultado (`docs/TESTING.md`) no existe todavía como archivo — lo genera
este mismo prompt la primera vez que lo ejecutas.
