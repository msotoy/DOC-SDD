# Plantilla — Prompt 01, Discovery

## Plantilla

```text
CONTEXTO
[Qué es este proyecto/módulo, en una frase: stack, archivos principales].
Lee primero README.md (cómo correrlo), RETO.md (o el equivalente: qué hay que
encontrar), REGLAS.md (reglas del laboratorio) y docs/ENDPOINTS.md si existe
(si no, genéralo tú a partir del código). NO EDITES CODIGO todavia.

OBJETIVO
Mapear [el flujo principal a explorar] y generar HALLAZGOS.md: una matriz con
cada hallazgo de RETO.md que exista realmente en el código, con evidencia
archivo + línea.

RESTRICCIONES
No modifiques ningún archivo de código. No des por cierto un hallazgo que no
puedas señalar en el código con archivo y línea. Respeta el contrato de
docs/ENDPOINTS.md: no propongas cambiarlo, solo corregirlo por dentro.

CRITERIOS DE ACEPTACION
Cada hallazgo de RETO.md queda en HALLAZGOS.md como una fila con: id (H-01, H-02...), hallazgo,
tipo (Vulnerabilidad / Bug / Refactor / Sugerencia — el que mejor lo
describa), explicación breve del riesgo, evidencia (archivo:línea), severidad
(alta/media/baja) y estado inicial "Pendiente". Ordenados de mayor a menor
severidad. Si algo de RETO.md no aparece en el código, se marca "No
encontrado" en vez de omitirse.

FORMATO DE RESPUESTA
El archivo HALLAZGOS.md, con la tabla: id | hallazgo | tipo | explicación |
evidencia | severidad | estado. Sin tocar código todavía.
```

## Ejemplo real ([ejercicios/auth-backend/1-discovery.md](../ejercicios/auth-backend/1-discovery.md))

```text
CONTEXTO
Backend Quarkus de autenticacion (AuthResource, LegacyDatabase,
LegacyTokenUtil, UserRecord). Lee primero README.md (como correrlo), RETO.md
(tabla de hallazgos esperados), REGLAS.md (reglas del laboratorio) y
docs/ENDPOINTS.md si existe (si no, genéralo a partir del codigo). NO
EDITES CODIGO todavia.

OBJETIVO
Mapear el flujo completo de login (validacion, persistencia, generacion de
token, configuracion) y generar HALLAZGOS.md: una matriz de seguimiento con
cada hallazgo de RETO.md que exista realmente en el codigo, con evidencia
archivo + linea.
```
