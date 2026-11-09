# Prompt 05 — Documentar y completar las pruebas (docs/TESTING.md)

Corre esto despues de 4-endpoints.md.

```text
AMBITO
Trabaja unicamente en la carpeta workshop-login-frontend/ de reqflow-workspace.
Todas las rutas de este prompt son relativas a esa carpeta. No leas ni
modifiques los otros repositorios del workspace.

CONTEXTO
Aplicacion Angular ya refactorizada. docs/ENDPOINTS.md ya refleja el contrato
real y detallado. Consulta ese archivo, REGLAS.md (meta de cobertura) y
cualquier otro documento que consideres necesario.

OBJETIVO
Generar docs/TESTING.md y completar las pruebas que falten para el flujo de
login y consulta de tareas, cubriendo tres categorias: camino feliz, casos
borde y errores.

RESTRICCIONES
No inventes flujos que no esten en docs/ENDPOINTS.md. No adaptes un test para
que pase con un bug existente: si encuentras un bug, repórtalo aparte, no lo
escondas dentro del test.

CRITERIOS DE ACEPTACION
Hay al menos: un test de camino feliz (login valido, tareas cargan), un test de
caso borde (usuario o contrasena vacios, respuesta sin token), y un test por
cada error documentado en docs/ENDPOINTS.md (backend caido, token invalido,
timeout). Cobertura del codigo modificado en 85% o superior.

FORMATO DE RESPUESTA
El archivo docs/TESTING.md con una tabla (flujo | caso | tipo | resultado
esperado) y despues el codigo de los tests, corriendo en verde. Al final, que
documentos consultaste.
```
