# Plantilla de prompt — adáptala a tu rol

Los prompts numerados (`1` a `5`) están en esta misma carpeta. Pero no van a
cubrir todo lo que necesites pedir. No importa si eres Chapter,
Backend, Frontend, QA/Cyber o Líder Técnico: para cualquier otra cosa que le
pidas a la IA hoy, usa las mismas 5 partes. Copia este bloque y completa cada
sección — no la saltes aunque parezca lento, es lo que convierte un pedido en
algo que se puede revisar.

```text
AMBITO
Trabaja unicamente en la carpeta workshop-login-frontend/ de reqflow-workspace.
Todas las rutas de este prompt son relativas a esa carpeta. No leas ni
modifiques los otros repositorios del workspace.

CONTEXTO
Qué existe ya (archivos, contrato, decisiones previas). En este repo, según lo
que necesites, consulta: REGLAS.md (reglas del laboratorio), RETO.md
(hallazgos a buscar), HALLAZGOS.md (estado de cada hallazgo),
docs/ENDPOINTS.md (contrato de API que consume esta app) o docs/GOOD_PRACTICES.md
(convenciones), o docs/TESTING.md (pruebas ya escritas).

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

- **Backend**: tu CONTEXTO casi siempre parte de `docs/ENDPOINTS.md` (el
  contrato que no puedes romper) y `docs/GOOD_PRACTICES.md` (cómo se espera que
  quede el código). Tus CRITERIOS suelen incluir un código de estado HTTP y un
  test.
- **Frontend**: tu CONTEXTO necesita saber qué endpoint consumes (también en
  `docs/ENDPOINTS.md`) y qué componente o servicio se ve afectado. Tus
  RESTRICCIONES suelen incluir "no cambies el contrato que ya consume el
  componente X".
- **QA / Cyber**: tu CONTEXTO parte de `HALLAZGOS.md` o `RETO.md`, no del
  código en sí. Tus CRITERIOS casi siempre piden evidencia (archivo:línea)
  antes que una corrección — primero confirmar, después arreglar.
- **Chapter / Líder Técnico**: tu CONTEXTO suele ser el estado general del
  repo (`HALLAZGOS.md`, `PLAN.md` si ya existe uno). Tu OBJETIVO suele ser
  priorizar o coordinar entre roles, no programar directamente — por ejemplo,
  pedirle a la IA que resuma el estado de `HALLAZGOS.md` para reportarlo al
  equipo.

## Si necesitas documentar algo que no entra en los archivos existentes

Si tu prompt genera documentación que no encaja en `docs/ENDPOINTS.md`,
`docs/GOOD_PRACTICES.md` ni `docs/TESTING.md` (por ejemplo, una decisión de
arquitectura, un diagrama, notas de una retro), pídele a la IA que cree un
archivo nuevo dentro de `docs/`, con un nombre corto y descriptivo (por
ejemplo `docs/DECISIONES.md`). Agrégalo después a la lista de abajo para que
el resto del equipo sepa que existe.

## Documentos de este repo

- `REGLAS.md` — reglas del laboratorio.
- `RETO.md` — hallazgos que hay que encontrar.
- `HALLAZGOS.md` — estado de cada hallazgo (Pendiente / Resuelto).
- `docs/ENDPOINTS.md` — contrato de los endpoints que consume esta app.
- `docs/GOOD_PRACTICES.md` — convenciones del código.
- `docs/TESTING.md` — qué se prueba y cómo.
- _(agrega aquí los que crees tú)_
