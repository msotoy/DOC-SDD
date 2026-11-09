# Plantilla — Prompt 04, Endpoints

Ejecuta esto cuando `HALLAZGOS.md` no tenga hallazgos "Pendiente" que hayas
decidido resolver (refactor y review ya mergeados).

## Plantilla

```text
CONTEXTO
[Tu proyecto], ya refactorizado. docs/ENDPOINTS.md tiene el contrato legacy
(defectos incluidos); hay que actualizarlo. Consulta el código y los
documentos que consideres necesarios. NO EDITES CODIGO, esto es solo
documentación.

OBJETIVO
Actualizar docs/ENDPOINTS.md para que alguien que nunca vio este proyecto
pueda integrar contra él sin leer el código fuente.

RESTRICCIONES
No inventes campos, tipos o códigos de respuesta que no existan en el
código. Si algo no está claro, márcalo como pregunta abierta.

CRITERIOS DE ACEPTACION
Por cada endpoint/función pública, docs/ENDPOINTS.md incluye:
1. Qué hace (una frase, en términos de negocio).
2. Si requiere autenticación y qué header exacto.
3. Request: tabla de campos + ejemplo real y completo.
4. Response exitosa: código de estado, tabla + ejemplo real.
5. Cada respuesta de error posible, con su cuerpo de ejemplo.
6. Notas de seguridad relevantes si aplica.

FORMATO DE RESPUESTA
El archivo docs/ENDPOINTS.md actualizado, siguiendo esa estructura de 6
puntos. Al final, qué documentos consultaste.
```

Ver el ejemplo real completo en [ejercicios/auth-backend/4-endpoints.md](../ejercicios/auth-backend/4-endpoints.md)
(y las versiones de los otros 2 repos, en esta misma carpeta).
El resultado (`docs/ENDPOINTS.md`) no existe todavía como archivo — lo genera
este mismo prompt la primera vez que lo ejecutas.
