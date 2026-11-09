# Prompt 01 — Discovery backend

```text
AMBITO
Trabaja unicamente en la carpeta workshop-auth-backend/ de reqflow-workspace.
Todas las rutas de este prompt son relativas a esa carpeta. No leas ni
modifiques los otros repositorios del workspace.

CONTEXTO
Backend Quarkus de autenticacion (AuthResource, LegacyDatabase, LegacyTokenUtil,
UserRecord). Lee primero README.md (como correrlo), RETO.md (tabla de hallazgos
esperados), REGLAS.md (reglas del laboratorio) y docs/ENDPOINTS.md si existe (si
no, genéralo a partir del codigo). NO EDITES CODIGO todavia.

OBJETIVO
Mapear el flujo completo de login (validacion, persistencia, generacion de token,
configuracion) y generar HALLAZGOS.md: una matriz de seguimiento con cada
hallazgo de RETO.md que exista realmente en el codigo, con evidencia archivo +
linea.

RESTRICCIONES
No modifiques ningun archivo de codigo. No des por cierto un hallazgo que no
puedas senalar en el codigo con archivo y linea. Respeta el contrato de
docs/ENDPOINTS.md: no propongas cambiarlo, solo corregirlo por dentro.

CRITERIOS DE ACEPTACION
Cada hallazgo de RETO.md queda en HALLAZGOS.md como una fila con: id (H-01, H-02...), hallazgo,
tipo (Vulnerabilidad / Bug / Refactor / Sugerencia — el que mejor describa el
hallazgo), explicacion breve del riesgo (que puede salir mal y por que),
evidencia (archivo:linea), severidad (alta/media/baja) y estado inicial
"Pendiente". Los hallazgos quedan ordenados de mayor a menor severidad. Si un
hallazgo de RETO.md no aparece en el codigo, se marca como "No encontrado" en
vez de omitirse.

FORMATO DE RESPUESTA
El archivo HALLAZGOS.md, con esta tabla:
id | hallazgo | tipo | explicacion | evidencia (archivo:linea) | severidad | estado
Sin tocar codigo todavia. HALLAZGOS.md es el unico lugar donde se lleva el
seguimiento: 2-refactor.md lo va a ir actualizando hallazgo por hallazgo.
```
