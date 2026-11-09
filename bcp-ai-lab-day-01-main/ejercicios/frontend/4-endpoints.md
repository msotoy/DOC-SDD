# Prompt 04 — Actualizar el contrato que consume (docs/ENDPOINTS.md)

Corre esto cuando `HALLAZGOS.md` no tenga items "Pendiente" que decidiste
resolver (refactor y review ya mergeados).

```text
AMBITO
Trabaja unicamente en la carpeta workshop-login-frontend/ de reqflow-workspace.
Todas las rutas de este prompt son relativas a esa carpeta. No leas ni
modifiques los otros repositorios del workspace.

CONTEXTO
Aplicacion Angular ya refactorizada. docs/ENDPOINTS.md tiene el flujo legacy
(defectos incluidos); hay que actualizarlo a como quedo el codigo hoy. Consulta
el codigo y los documentos del repositorio que consideres necesarios para
verificar cada campo. NO EDITES CODIGO, esto es solo documentacion.

OBJETIVO
Actualizar docs/ENDPOINTS.md para que un desarrollador que nunca vio esta
aplicacion entienda, sin leer el codigo fuente, que envia y que espera recibir
de cada endpoint externo que consume.

RESTRICCIONES
No inventes campos o comportamientos que no existan en el codigo. Si algo no
esta claro leyendo el codigo, márcalo como pregunta abierta. No documentes cada
endpoint con una sola linea: sigue la estructura de abajo completa.

CRITERIOS DE ACEPTACION
Por cada endpoint consumido (login, tareas), docs/ENDPOINTS.md incluye TODO lo
siguiente (nada es opcional):
1. Quien lo llama (que componente o servicio).
2. Que envia: headers, body o query params, con tabla y ejemplo real.
3. Que espera recibir en exito: codigo de estado, tabla de campos, ejemplo real.
4. Como reacciona ante cada error posible (token invalido, timeout, respuesta
   inesperada): que hace la UI en cada caso, no solo "puede fallar".
5. Notas de seguridad relevantes (por ejemplo, que ya no se usa `[innerHTML]`
   sin sanitizar, o donde vive ahora el manejo de sesion).
Cada campo y cada ejemplo tienen que poder verificarse contra el codigo real.

FORMATO DE RESPUESTA
El archivo docs/ENDPOINTS.md actualizado, siguiendo exactamente esa estructura
de 5 puntos por endpoint. Al final, que documentos consultaste.
```
