# Prompt 03 — Code review

```text
AMBITO
Trabaja unicamente en la carpeta workshop-login-frontend/ de reqflow-workspace.
Todas las rutas de este prompt son relativas a esa carpeta. No leas ni
modifiques los otros repositorios del workspace.

CONTEXTO
El PR implementa uno o mas items de HALLAZGOS.md. Consulta los documentos del
repositorio que consideres necesarios para justificar cada observacion (por
ejemplo README.md, RETO.md, docs/ENDPOINTS.md, docs/GOOD_PRACTICES.md,
REGLAS.md) y al final dime cuales usaste.

OBJETIVO
Revisar el PR como lider tecnico, evaluando seguridad, mantenibilidad,
accesibilidad, manejo de estado, errores, pruebas y dependencias. Verificar que
cada item marcado "Resuelto" en HALLAZGOS.md este realmente corregido.

RESTRICCIONES
No apruebes cambios que silencien scanners, reduzcan quality gates, o muevan
secretos al frontend. No inventes riesgos que no puedas senalar con archivo y
linea.

CRITERIOS DE ACEPTACION
Cada item "Resuelto" de HALLAZGOS.md queda verificado con evidencia, o se
regresa a "Pendiente" si el PR no lo corrigio del todo. Se confirma en
especifico que ya no hay `[innerHTML]` con datos sin sanitizar ni `any` en el
codigo modificado.

FORMATO DE RESPUESTA
Observaciones clasificadas en bloqueantes, importantes y sugerencias. Para cada
bloqueante: por que bloquea el merge y que evidencia lo respalda. Si algun item
vuelve a "Pendiente", dilo explicitamente. Al final, que documentos
consultaste.
```

Si encontraste algo que no estaba en `HALLAZGOS.md` (un bug nuevo, una
sugerencia importante), agrégalo ahí mismo como una fila nueva con estado
"Pendiente" — no lo dejes solo mencionado en el chat. Se resuelve después con
[resolver-item.md](resolver-item.md), igual que cualquier otro item.
