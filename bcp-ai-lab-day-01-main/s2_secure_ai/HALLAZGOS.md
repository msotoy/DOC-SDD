# Plantilla — HALLAZGOS.md

No se copia vacío ni se llena a mano: lo genera
[discovery.md](../ejercicios/auth-backend/1-discovery.md)
la primera vez que lo ejecutas, leyendo tu código real y la tabla de
[RETO.md](https://github.com/NTTData-Academy/workshop-auth-backend-template/blob/instructor/RETO.md). Esto es solo el formato
que tiene que respetar.

## Formato

```
| Id | Hallazgo | Tipo | Explicación | Evidencia | Severidad | Estado |
|---|---|---|---|---|---|---|
| H-01 | [qué es] | Vulnerabilidad / Bug / Refactor / Sugerencia | [por qué es un riesgo o problema, en una frase] | [archivo:línea] | alta/media/baja | Pendiente / Resuelto / No encontrado |
```

La columna **Tipo** clasifica cada hallazgo, no solo su severidad:

- **Vulnerabilidad** — riesgo de seguridad (inyección, autorización ausente, datos expuestos).
- **Bug** — el comportamiento actual no es el esperado, sin ser un tema de seguridad.
- **Refactor** — el código funciona bien, pero viola una regla de Clean Code (duplicación, responsabilidad mezclada, anidamiento).
- **Sugerencia** — una mejora opcional, no bloqueante.

Reglas de este archivo, sin importar el proyecto:

- El **Id** (`H-01`, `H-02`…) no cambia nunca: el Día 2 lo usa para enlazar
  cada historia de usuario e issue con su hallazgo de origen.

- Un hallazgo sin evidencia (archivo:línea) no es un hallazgo, es una
  suposición — no debería quedar así.
- "Resuelto" siempre va acompañado de una nota corta (1-2 líneas) de cómo se
  resolvió y qué test lo respalda.
- Si algo esperado no aparece en el código, se marca "No encontrado" — no se
  omite la fila.

## Ejemplo real (una fila de `HALLAZGOS.md` después de correr `discovery.md`)

```
| H-01 | SQL concatenado en LegacyDatabase.findByCredentials | Vulnerabilidad | Permite inyección SQL si el input no se sanitiza | LegacyDatabase.java:46 | alta | Resuelto — PreparedStatement con parámetros (PR #3, test LegacyDatabaseTest.rechazaInyeccionSql) |
```
