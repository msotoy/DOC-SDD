# Prompt 04 — Actualizar el contrato (docs/ENDPOINTS.md)

Corre esto cuando `HALLAZGOS.md` no tenga hallazgos "Pendiente" (refactor y
review ya mergeados).

```text
AMBITO
Trabaja unicamente en la carpeta workshop-auth-backend/ de reqflow-workspace.
Todas las rutas de este prompt son relativas a esa carpeta. No leas ni
modifiques los otros repositorios del workspace.

CONTEXTO
Backend Quarkus de autenticacion, ya refactorizado. docs/ENDPOINTS.md tiene el
contrato legacy (defectos incluidos); hay que actualizarlo a como quedo el
codigo hoy. Consulta el codigo y los documentos del repositorio que consideres
necesarios para verificar cada campo. NO EDITES CODIGO, esto es solo
documentacion.

OBJETIVO
Actualizar docs/ENDPOINTS.md para que un desarrollador que nunca vio este
backend pueda integrar contra el sin leer el codigo fuente.

RESTRICCIONES
No inventes campos, tipos o codigos de respuesta que no existan en el codigo. Si
algo no esta claro leyendo el codigo, márcalo como pregunta abierta en vez de
asumirlo. No documentes "GET /q/health" y "POST /auth/login" con una sola linea
cada uno: sigue la estructura de abajo completa.

CRITERIOS DE ACEPTACION
Por cada endpoint, docs/ENDPOINTS.md incluye TODO lo siguiente (nada es
opcional):
1. Que hace (una frase, en terminos de negocio, no solo tecnicos).
2. Si requiere autenticacion y que header exacto.
3. Request: una tabla campo | tipo | obligatorio | descripcion, mas un ejemplo
   JSON real y completo.
4. Response exitosa: codigo de estado, tabla campo | tipo | descripcion, mas un
   ejemplo JSON real y completo.
5. Cada respuesta de error posible: codigo de estado, cuando ocurre, y un
   ejemplo de cuerpo de esa respuesta (no solo "puede fallar").
6. Notas de seguridad relevantes si aplica (por ejemplo, que el token ahora es
   firmado y expira de verdad).
Cada campo y cada ejemplo tienen que poder verificarse contra el codigo real
(archivo + linea si hace falta justificarlo).

FORMATO DE RESPUESTA
El archivo docs/ENDPOINTS.md actualizado, siguiendo exactamente esa estructura
de 6 puntos por endpoint. Al final, que documentos consultaste para escribirlo.
```
