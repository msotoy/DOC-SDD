# Laboratorio S1 - Skill básico

**Horario:** 09:30 - 11:30 (2 h)
**Objetivo:** Crear un Skill reutilizable que convierta una feature request en un paquete mínimo trazable, usando Metadata, I/O y constraints.

## Materiales

- Skill: `feature-intake-spec-checklist`, versión `0.1.0`.
- Ruta estándar del repositorio: `.github/skills/`.
- `reqflow-workspace/` del Dia 1 abierto en VS Code, con acceso a Copilot Chat. S1 se trabaja dentro de `workshop-auth-backend/`: todas las rutas relativas de esta guia parten de ahi.
- Git y un IDE con soporte Markdown.
- Tu `HALLAZGOS.md` y `prompts/` del Dia 1 (ver "Entrada del dia" en el README).

> Usar este Skill antes de crear tareas de implementación o abrir un PR significativo.

## Pasos

### 01. Crear estructura del Skill

**Tiempo estimado:** 5 minutos.

Crea el Skill en la ruta estándar `.github/skills/` de `workshop-auth-backend` (el repo de la HU-01). Un Skill de Copilot se define como una carpeta con un archivo `SKILL.md` (contrato) y ejemplos de entrada/salida que documentan su uso esperado.

```bash
# Bash
mkdir -p .github/skills/feature-intake-spec-checklist/examples
touch .github/skills/feature-intake-spec-checklist/SKILL.md
touch .github/skills/feature-intake-spec-checklist/examples/input.sample.md
touch .github/skills/feature-intake-spec-checklist/examples/output.sample.md
```

```powershell
# PowerShell
New-Item -ItemType Directory -Force .github\skills\feature-intake-spec-checklist\examples
New-Item -ItemType File -Force .github\skills\feature-intake-spec-checklist\SKILL.md
New-Item -ItemType File -Force .github\skills\feature-intake-spec-checklist\examples\input.sample.md
New-Item -ItemType File -Force .github\skills\feature-intake-spec-checklist\examples\output.sample.md
```

**Salida esperada:** tres archivos existen bajo `.github/skills/feature-intake-spec-checklist/` — `SKILL.md`, `examples/input.sample.md`, `examples/output.sample.md` — sin que su contenido esté completo aún.

### 02. Completar el contrato

**Tiempo estimado:** 30-40 minutos.

Abre `SKILL.md`, elimina su contenido y pega la plantilla; reemplaza los `[EDITAR]` o marca "Pendiente de confirmar". El frontmatter (`name` + `description`) es el mínimo requerido por Copilot para descubrir el Skill; el resto del documento (Metadata, Inputs, Output, Constraints, Validation Rules, Evidence) es la convención interna que hace el contrato auditable y consistente entre roles.

```markdown
---
name: feature-intake-spec-checklist
description: Estandariza la definición de funcionalidades antes de la implementación generando un paquete mínimo trazable que cubra alcance, decisiones, riesgos, criterios de aceptación y planes de validación.
---

# Skill: Feature Intake -> Spec Checklist

## 1) Metadata
- **Skill ID:** feature-intake-spec-checklist
- **Version:** 0.1.0
- **Purpose:** Estandarizar la definición de funcionalidades antes de la implementación generando un paquete mínimo trazable que cubra alcance, decisiones, riesgos, aceptación y validación.
- **Audience (roles):** Chapter/PO, Tech Lead, Backend, Frontend, QA, Cyber
- **When to use:** Antes de crear tareas de implementación o abrir un PR significativo.
- **When NOT to use:** Incidentes P1 de producción, cambios triviales como typos o tareas sin impacto funcional.
- **Sensitive inputs:** No incluyas datos reales de clientes, credenciales, secretos, tokens ni URLs internas no autorizadas.
- **Expected output:** Markdown estructurado mediante la sección Output a continuación.

## 2) Inputs
Proporciona la información en este formato:

- **Business context (brief):**
- **Feature request / user story:**
- **Expected impact (metric or outcome):**
- **Scope (in/out):**
- **Known technical constraints:** (stack, standards, performance, availability)
- **Known risks:** (security, compliance, stability)
- **Dependencies:** (services, teams, data)
- **Team Definition of Done (DoD):** (if available)

## 3) Output
Devuelve **solo** un documento Markdown con estas secciones y bullets:

1. **Summary**
2. **Scope**
    - Dentro del alcance
    - Fuera del alcance
3. **Supuestos**
4. **Decisiones técnicas por tomar (pendientes o resueltas)**
5. **Riesgos y mitigaciones**
6. **Criterios de aceptación (medibles)**
7. **Plan de validación**
    - Pruebas unitarias
    - Pruebas funcionales
    - Seguridad (comprobaciones mínimas)
    - Evidencia requerida (qué adjuntar)
8. **Tareas sugeridas por rol**
    - Chapter/PO
    - Tech Lead
    - Backend
    - Frontend
    - QA
    - Cyber
9. **Preguntas abiertas**

## 4) Constraints
- No inventes requisitos: si falta información, inclúyela bajo **Preguntas abiertas**.
- No propongas herramientas fuera del stack permitido.
- No incluyas datos sensibles ni secretos.
- Los criterios de aceptación deben ser verificables; no escribas "mejorar el rendimiento" sin una métrica.
- El plan de validación debe incluir al menos un elemento de evidencia concreto, como salida de pruebas, un checklist o un archivo actualizado.
- Mantén la salida en un máximo de 1-2 páginas para que siga siendo usable.

## 5) Validation Rules
La salida es válida si:
- Incluye todas las secciones definidas en Output.
- Tiene al menos 3 criterios de aceptación medibles.
- Tiene al menos 3 tareas para cada rol central: Tech Lead, Backend y QA, o explica por qué un rol no aplica.
- Incluye al menos 2 riesgos con mitigaciones.
- No contiene datos sensibles ni secretos.
- No contiene supuestos no declarados.

## 6) Evidence
Adjunta o referencia estos elementos en el PR o entrega:
- `SKILL.md` versionado.
- `examples/input.sample.md`.
- `examples/output.sample.md`.
- Tag de versión para el Skill, como `skill-feature-intake-v0.1.0`.
```

**Criterio de salida:** otro rol debe poder leer el archivo y saber qué activa el Skill, qué información recibe, qué devuelve, qué límites respeta y cómo se valida.

### 03. Crear entrada

**Tiempo estimado:** 5-10 minutos.

Pega el caso de ejemplo en `examples/input.sample.md`; puedes adaptar contexto, impacto o dependencias, conservando los ocho encabezados definidos en la sección `Inputs` del contrato.

> **Conexión con el Día 1:** el Skill es la versión reutilizable de lo que hiciste ayer a mano con tus prompts de `prompts/`. Para que el ejemplo sea real, basa el caso en una fila "Pendiente" de tu `HALLAZGOS.md`: la explicación del riesgo va a contexto e impacto, y la evidencia (`archivo:línea`) va a dependencias.

```markdown
## Business context (brief)
Reduce complaints caused by duplicate transfers.

## Feature request / user story
As a user, I want to confirm a transfer before sending it
so that I can avoid duplicates.

## Expected impact
Reduce duplicate-transfer complaints by 20% in one month.

## Scope (in/out)
In: pre-send confirmation, summary message, data validation.
Out: infrastructure changes and a complete UI redesign.

## Known technical constraints
Existing REST API, web frontend, standardized logging.

## Known risks
Sensitive data exposure in logs; amount-validation errors.

## Dependencies
Accounts service and transfers service.

## Team Definition of Done (DoD)
Unit tests, brief documentation, and reviewed PR.
```

**Criterio de salida:** la entrada es suficientemente concreta para generar una especificación sin inventar requisitos; lo no confirmado queda como pregunta abierta.

### 04. Crear salida

**Tiempo estimado:** 10-15 minutos.

Genera `examples/output.sample.md` a partir de la entrada; puedes cambiar decisiones, riesgos o tareas pero no elimines secciones del contrato.

```markdown
# Feature Intake -> Spec Checklist

## 1. Summary
Add a pre-send transfer confirmation with a concise summary
and validation of transfer data. Target: 20% reduction in
duplicate-transfer complaints in one month.

## 6. Acceptance criteria (measurable)
- 95%+ of valid attempts show confirmation before submission.
- Invalid data blocks submission with a validation message.
- Duplicate complaints drop 20% within one month.
- No sensitive values appear in confirmation event logs.

## 9. Open questions
- What baseline measures the 20% reduction?
- Which API version owns the confirmation contract?
```

**Criterio de salida:** documento Markdown de 1-2 páginas, accionable, sin decisiones no sustentadas por la entrada o una decisión humana.

### 05. Demostrar y versionar el Skill

**Tiempo estimado:** 15-20 minutos.

Demuestra que el Skill es descubrible y ejecutable antes de versionarlo.

**1. Listar los skills configurados:**

```bash
# Bash
find .github/skills -maxdepth 2 -type f
```

```powershell
# PowerShell
Get-ChildItem -Recurse .github\skills | Select-Object FullName
```

**Salida esperada:** el listado muestra `feature-intake-spec-checklist/SKILL.md` y sus dos ejemplos; esto confirma que el Skill está en la ruta que Copilot descubre automáticamente en el repositorio.

**2. Prompt para ejecutar el Skill (Copilot Chat):**

```text
Actua como el Skill feature-intake-spec-checklist
(.github/skills/feature-intake-spec-checklist/SKILL.md).
Usa como entrada el contenido de examples/input.sample.md y genera
UNICAMENTE el documento Output definido en el contrato del Skill.
```

**Salida esperada:** Copilot Chat responde con un único documento Markdown con las nueve secciones del contrato (Summary, Scope, Assumptions ... Open questions), coherente con `examples/output.sample.md` y sin inventar datos fuera de la entrada.

**3. Commit y tag:**

```bash
git add .github/skills/feature-intake-spec-checklist
git commit -m "Add basic skill: feature intake to spec checklist (v0.1.0)"
git tag skill-feature-intake-v0.1.0
```

> El tag de versión (`skill-feature-intake-v0.1.0`) es la evidencia de trazabilidad que exige la sección `Evidence` del contrato: permite referenciar exactamente qué versión del Skill produjo un resultado dado.

**Criterio de salida:** el Skill es descubrible en `.github/skills/`, produce el documento esperado al invocarlo desde Copilot Chat, y queda versionado con commit y tag.

### 06. Aplicar el Skill a la HU-01

**Tiempo estimado:** 15-20 minutos.

`HU-01.md` no se copia: se genera desde el `HALLAZGOS.md` de tu `workshop-auth-backend` del Día 1. Busca las filas "Pendiente" sobre el token (sin firma, sin expiración real o con un secreto por defecto) y pide la HU en la raíz de `workshop-auth-backend`:

```text
CONTEXTO
workshop-auth-backend/HALLAZGOS.md es la matriz de hallazgos del Dia 1.

OBJETIVO
Generar workshop-auth-backend/HU-01.md a partir de las filas "Pendiente"
de HALLAZGOS.md relacionadas con el token de autenticacion.

RESTRICCIONES
No inventes hallazgos que no esten en HALLAZGOS.md. No incluyas valores de
tokens, secretos ni credenciales.

CRITERIOS DE ACEPTACION
HU-01.md tiene las secciones Origen, Contexto, Ajustes necesarios, Criterios de
aceptacion y Evidencia esperada. Origen lista los Id (H-xx) y la evidencia
archivo:linea de cada hallazgo usado. Cada criterio de aceptacion es
verificable con una prueba.

FORMATO DE RESPUESTA
Solo el archivo HU-01.md.
```

Si tu `HALLAZGOS.md` no tiene hallazgos de token en estado "Pendiente", copia la versión de referencia:

```powershell
Copy-Item ..\..\bcp-ai-lab-day-02\s1_skills\HU-01.md .\HU-01.md
```

Verifica que el archivo local exista antes de ejecutar el Skill:

```powershell
Test-Path .\HU-01.md
```

El archivo contiene la historia, criterios de aceptación y evidencia que se utilizarán en este paso.

**Comprobación:** confirma que el archivo existe y que Copilot Chat puede leerlo desde la raíz del repositorio.

```bash
# Bash
test -f HU-01.md && cat HU-01.md
```

```powershell
# PowerShell
Test-Path .\HU-01.md
Get-Content .\HU-01.md
```

**Prueba:** genera tu prompt para usar este Skill con el archivo creado (`HU-01.md`). Puedes también usar el siguiente prompt:

```text
Actua como el Skill feature-intake-spec-checklist
(.github/skills/feature-intake-spec-checklist/SKILL.md).

Lee workshop-auth-backend/HU-01.md y usa el archivo como unica entrada.
Genera UNICAMENTE el documento Output definido en el contrato del Skill,
con sus nueve secciones: Summary, Scope (in/out), Assumptions,
Technical decisions to make, Risks and mitigations, Acceptance criteria,
Validation plan, Suggested tasks by role y Open questions.

No inventes requisitos. Marca como pregunta abierta toda decision que la HU
no confirme. No incluyas valores de tokens, secretos ni credenciales.
```

**Revisar el resultado:** verifica que la respuesta cubra los claims `sub`, `client`, `iat` y `exp`; la relación entre `expiresIn` y `exp`; la configuración segura de `AUTH_TOKEN_SECRET`; ausencia de logs sensibles; pruebas de token, expiración y claims; y tareas para Tech Lead, Backend y QA. La decisión HMAC frente a una librería JWT debe quedar como una decisión técnica o pregunta abierta, no como un hecho inventado.

**Criterio de salida:** `HU-01.md` está versionado en la raíz, el Skill lee el archivo como entrada y produce un documento trazable, sin secretos, con criterios de aceptación verificables y preguntas abiertas donde falte confirmación.

## Qué obtengo

- `.github/skills/feature-intake-spec-checklist/` con `SKILL.md`, `examples/input.sample.md`, `examples/output.sample.md`.
- Demostración de descubrimiento y ejecución del Skill desde Copilot Chat.
- `HU-01.md` revisada por el Skill y un resultado trazable de contrato y seguridad.
- Commit y tag `skill-feature-intake-v0.1.0`.
