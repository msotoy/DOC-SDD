# Laboratorio S2 - Skills desde el catálogo (onboarding + ciclo SDLC)

**Horario:** 11:45 - 13:00 (1 h 15)
**Objetivo:** Registrar tu repositorio en el catálogo central `skills-catalog`, instalar los Skills base de ReqFlow (los mismos usados en el Día 3) vía ISSUE y simular un ciclo SDLC gobernado (Discovery → Spec → Architecture → Implementation → DoD) sobre los tres workshops.

## Materiales

- `reqflow-workspace/` del Dia 1 con tus 3 repos propios: `workshop-auth-backend`, `workshop-login-frontend`, `workshop-requirements-api`. Los comandos de esta guia se ejecutan desde `reqflow-workspace/`.
- `workshop-auth-backend/.github/skills/feature-intake-spec-checklist` ya creado en S1.
- Acceso para crear ISSUES en `NTTData-Academy/bcp-ai-skill-catalog` (plantillas `repo-onboarding` y `skills-install`).
- HU-01 (backend, token firmado), generada desde tu `HALLAZGOS.md` del Dia 1 en `HU-01.md` (version de referencia mas abajo).
- HU-05 (frontend, `innerHTML`), generada desde tu `HALLAZGOS.md` del Dia 1 en `HU-05.md` (version de referencia mas abajo).
- Skills del catálogo a instalar (set base ReqFlow; se reutiliza en el Día 3): `discovery-analysis` (quality), `spec-writing` (specification), `architecture-decision` (architecture), `issue-implementation` (quality), `reqflow-definition-of-done` (review).

> A diferencia de S1, aquí los Skills no se escriben a mano: se solicitan mediante ISSUES al catálogo central (`skills-catalog`) y un workflow los copia automáticamente a `.github/skills/` de tu repositorio, registrando además el repositorio y sus dominios en `subscribers.json`.

Antes de comenzar, ten las dos historias de usuario en la raíz de su repo. Los prompts y Skills de este módulo leen esos archivos locales:

- `workshop-auth-backend/HU-01.md` ya existe: la generaste en S1 (paso 06) desde tu `HALLAZGOS.md` del backend.
- `workshop-login-frontend/HU-05.md` se genera igual, con el mismo prompt de S1 paso 06, pero leyendo `workshop-login-frontend/HALLAZGOS.md` y buscando el hallazgo de `innerHTML` / mensajes de error en estado "Pendiente".
- En S2 los Skills también reciben `docs/ENDPOINTS.md` (contrato API) y `docs/TESTING.md` (matriz de pruebas) de tus repos del Día 1 como punto de partida, en vez de empezar de cero.

Solo si tu `HALLAZGOS.md` no tiene esos hallazgos "Pendiente", crea los archivos y pega el contenido de referencia de abajo:

```bash
touch workshop-auth-backend/HU-01.md
touch workshop-login-frontend/HU-05.md
```

En PowerShell:

```powershell
New-Item -ItemType File -Force .\workshop-auth-backend\HU-01.md
New-Item -ItemType File -Force .\workshop-login-frontend\HU-05.md
Test-Path .\workshop-auth-backend\HU-01.md
Test-Path .\workshop-login-frontend\HU-05.md
```

Pega este contenido de referencia en `workshop-auth-backend/HU-01.md`:

```markdown
# HU-01 - Token firmado con expiracion y claims minimos

## Origen

- Hallazgos de token del backend en `HALLAZGOS.md` (Id `H-xx` de tu Dia 1).

## Veredicto

**Usable con ajustes.** La historia conecta seguridad, configuracion, testing y evidencia.

## Contexto

El servicio de autenticacion expone `POST /auth/login` y devuelve `token`, `expiresIn` y `user`. La implementacion usa firma HMAC y lee `AUTH_TOKEN_SECRET`.

## Ajustes necesarios

- Exigir los claims `sub`, `client`, `iat` y `exp`.
- Obtener `client` desde la solicitud, validarlo y reflejarlo en el token.
- Comprobar que `expiresIn` coincide con `exp - now` usando una tolerancia documentada.
- Eliminar el secreto por defecto fuera del sandbox o documentarlo como exclusivo de laboratorio.
- Evitar logs del token y del secreto.
- Mantener como decision tecnica si se conserva HMAC o se adopta una libreria JWT.

## Criterios de aceptacion

- Un token valido contiene `sub`, `client`, `iat` y `exp`.
- `expiresIn` es coherente con `exp - now` dentro de la tolerancia definida.
- Login valido, credenciales invalidas y token expirado tienen pruebas.
- No se registran tokens, secretos ni valores sensibles.
- La decision sobre HMAC frente a una libreria JWT queda documentada.

## Evidencia esperada

- Documento generado por los Skills a partir de este archivo.
- Pruebas de claims, expiracion y errores de autenticacion.
- Configuracion documentada de `AUTH_TOKEN_SECRET`.
- Evidencia de logs redactados.
```

Pega este contenido de referencia en `workshop-login-frontend/HU-05.md`:

```markdown
# HU-05 - Eliminar `innerHTML` en mensajes de login

## Origen

- Hallazgo de `innerHTML` del frontend en `HALLAZGOS.md` (Id `H-xx` de tu Dia 1).

## Veredicto

**Usable directamente.** El hallazgo existe y el cambio es acotado, observable y facil de probar.

## Estado actual

`login.component.html` usa `[innerHTML]` para renderizar `message`, y `login.component.ts` construye mensajes con etiquetas HTML.

## Ajustes recomendados

- Cambiar el mensaje a texto plano.
- Usar interpolacion Angular: `{{ message }}`.
- Eliminar `<strong>` y `<br>` de los valores dinamicos.
- Mapear 400, 401 y 500 a mensajes genericos.
- Mantener detalles tecnicos solo en logs controlados, sin credenciales.

## Criterios de aceptacion

- No existe `[innerHTML]` en el flujo de login.
- Los mensajes se muestran como texto plano.
- Errores backend se convierten a mensajes genericos.
- Hay al menos una prueba para el mapeo de errores.
- El login valido y el logout no se rompen.

## Uso en el Dia 2

- S1: Skill de seguridad frontend.
- S2: template de cambio y pruebas.
- S3: tool de busqueda de patrones inseguros.
- W1: evidencia de diff, test y comportamiento.
```

## Pasos

### 01. Verificar prerrequisitos: workshops y Skill de S1

**Tiempo:** 5 minutos.

Desde `reqflow-workspace/`, confirma que los tres repos y el Skill de S1 existen antes de continuar. Este chequeo evita que un ISSUE de instalación falle a medias por rutas inexistentes.

```bash
# Bash
test -d workshop-auth-backend && echo "OK: workshop-auth-backend"
test -d workshop-login-frontend && echo "OK: workshop-login-frontend"
test -d workshop-requirements-api && echo "OK: workshop-requirements-api"
test -d workshop-auth-backend/.github/skills/feature-intake-spec-checklist && echo "OK: skill de S1"
```

```powershell
# PowerShell
Test-Path .\workshop-auth-backend
Test-Path .\workshop-login-frontend
Test-Path .\workshop-requirements-api
Test-Path .\workshop-auth-backend\.github\skills\feature-intake-spec-checklist
```

Si falta alguno de los repos, no clones la plantilla limpia: créalo como repo propio con el paso 1 del README del Día 1, o parte de la rama `checkpoint/day1`.

**Salida esperada:** los cuatro `test` (o `Test-Path`) confirman presencia.

### 02. Onboarding del repositorio en el catálogo

**Tiempo:** 10-15 minutos.

Antes de instalar Skills, tu repositorio debe existir en `subscribers.json` del catálogo. El ISSUE se crea desde el navegador (GitHub Issue Forms), sin marcar ningún dominio: eso se registrará solo más adelante, cuando instales los Skills en el paso 04.

1. Abre tu navegador de preferencia y ve a: `https://github.com/NTTData-Academy/bcp-ai-skill-catalog/issues`
2. Haz clic en **New issue** y selecciona la plantilla **Onboarding de nuevo repositorio**.
3. Revisa que el label `repo-onboarding` quede preseleccionado (campo **Labels** en la barra lateral del ISSUE).
4. En el campo **Repositorios destinos** escribe tus tres repos, sin el owner y uno por línea: `workshop-auth-backend`, `workshop-login-frontend`, `workshop-requirements-api`.
5. En **Dominios iniciales (Opcional)** no marques ninguna casilla: para este laboratorio los dominios se registran automáticamente al instalar los Skills en el paso 04.
6. Haz clic en **Submit new issue**.

> Detrás del formulario corre el workflow `onboard-repo-on-issue.yml`: parsea el cuerpo del ISSUE, copia el workflow consumidor a tu repositorio y actualiza el registro central. Es la misma lógica que dispararía un `workflow_dispatch` manual, pero activada por el ISSUE.

**Salida esperada:** el workflow `onboard-repo-on-issue.yml` se ejecuta, agrega `.github/workflows/sync-skills.yml` a tu repositorio, registra tu repositorio (con dominios `[]`) en `subscribers.json`, comenta el resultado en el ISSUE y lo cierra automáticamente si todo fue correcto.

### 03. Explorar el catálogo de Skills disponibles

**Tiempo:** 5-10 minutos.

Consulta `SKILLS-MANIFEST.json` filtrando los dominios que usarás en este laboratorio: api, backend, frontend, test, governance y review. El manifiesto es la fuente de verdad que resuelve `identifier -> domain -> path`, usada tanto por ti como por el workflow de instalación.

```bash
# Bash
curl -s https://raw.githubusercontent.com/NTTData-Academy/bcp-ai-skill-catalog/main/SKILLS-MANIFEST.json \
  | jq -r '.skills[] | select(.domain=="api" or .domain=="backend" or .domain=="frontend" or .domain=="test" or .domain=="governance" or .domain=="review") | "\(.domain) -> \(.identifier): \(.description)"'
```

```powershell
# PowerShell
$manifest = Invoke-RestMethod https://raw.githubusercontent.com/NTTData-Academy/bcp-ai-skill-catalog/main/SKILLS-MANIFEST.json
$manifest.skills |
  Where-Object { $_.domain -in @('api','backend','frontend','test','governance','review') } |
  Select-Object domain, identifier, description
```

**Salida esperada:** identificas, entre otros, `discovery-analysis`, `spec-writing`, `architecture-decision`, `issue-implementation` y `reqflow-definition-of-done`, que son los que instalarás en el siguiente paso.

### 04. Solicitar la instalación de los Skills base de ReqFlow (los mismos del Día 3)

**Tiempo:** 10-15 minutos.

Crea el ISSUE desde el navegador y marca exactamente los Skills del set base.

1. En `https://github.com/NTTData-Academy/bcp-ai-skill-catalog/issues`, haz clic en **New issue** y selecciona la plantilla **Instalar / actualizar Skills en un repositorio**.
2. Revisa que el label `skills-install` quede preseleccionado.
3. En **Repositorios destinos** escribe los mismos tres repos usados en el paso 02.
4. Marca solo estas casillas:
   - **Dominio: architecture** → `architecture-decision`
   - **Dominio: quality** → `discovery-analysis` y `issue-implementation`
   - **Dominio: review** → `reqflow-definition-of-done`
   - **Dominio: specification** → `spec-writing`
5. Deja sin marcar el resto de casillas y secciones de dominio. Haz clic en **Submit new issue**.

Si por algún motivo tu repositorio no quedó registrado en el paso 02, el workflow `install-skills-on-issue.yml` lo detecta y dispara el onboarding automáticamente antes de instalar los Skills (es una salvaguarda, no reemplaza el paso 02).

**Salida esperada:** `install-skills-on-issue.yml` crea un commit por Skill y hace push a la rama por defecto de tu repositorio, actualiza los dominios en `subscribers.json`, comenta el resultado en el ISSUE y lo cierra si todo fue correcto.

### 05. Sincronizar los Skills instalados en tu equipo

**Tiempo:** 5 minutos.

Los commits los crea el bot del catálogo directamente en tu repositorio remoto; trae esos cambios a tu clon local con un `pull` antes de seguir trabajando.

```bash
# Bash, desde reqflow-workspace/
for r in workshop-auth-backend workshop-login-frontend workshop-requirements-api; do
  git -C "$r" pull origin main
  find "$r/.github/skills" -maxdepth 1 -type d
done
```

```powershell
# PowerShell, desde reqflow-workspace/
foreach ($r in "workshop-auth-backend", "workshop-login-frontend", "workshop-requirements-api") {
    git -C $r pull origin main
    Get-ChildItem "$r\.github\skills"
}
```

**Salida esperada:** junto a `feature-intake-spec-checklist` (S1), ahora ves 5 carpetas nuevas: `discovery-analysis`, `spec-writing`, `architecture-decision`, `issue-implementation` y `reqflow-definition-of-done`.

### 06. Discovery - Encontrar hallazgos y seleccionar un issue candidato (sin cambiar código)

**Tiempo:** 10-15 minutos.

Usa `discovery-analysis` para analizar el producto ReqFlow (multi-repo) y producir una lista corta de hallazgos con evidencia. La salida se usa para decidir un Issue candidato (routing/HITL), no para arreglarlo automáticamente.

```text
Actua como el Skill discovery-analysis
(.github/skills/discovery-analysis/SKILL.md).

Contexto: estas en reqflow-workspace/ con los tres repos:
- workshop-auth-backend
- workshop-login-frontend
- workshop-requirements-api

Objetivo: produce 3-5 hallazgos con evidencia concreta (archivo:linea o comando),
impacto, prioridad propuesta, contrato potencialmente afectado y como validarlo.

Restricciones:
- no modificar codigo;
- no crear issues automaticamente;
- marca todo como CANDIDATO y detente para revision humana.
```

**Salida esperada:** 3-5 hallazgos con evidencia (Estado: CANDIDATO) listos para convertir en Issue tras gate humano.

### 07. Spec - Especificar el cambio aprobado

**Tiempo:** 10-15 minutos.

Una vez que el equipo seleccione un hallazgo/Issue candidato, usa `spec-writing` para convertirlo en spec verificable (sin diseño ni implementación).

```text
Actua como el Skill spec-writing
(.github/skills/spec-writing/SKILL.md).

Fuente: usa como entrada el hallazgo/Issue aprobado (titulo + evidencia + impacto).
Incluye contratos protegidos de ReqFlow cuando aplique.

Entrega solo la spec en el formato sugerido por el Skill y detente para
revision humana.
```

**Salida esperada:** spec verificable con alcance, fuera de alcance, criterios de aceptación y contratos protegidos.

### 08. Architecture - Decidir estrategia y pruebas a proteger

**Tiempo:** 10-15 minutos.

Usa `architecture-decision` para evaluar impacto, estrategia incremental y pruebas necesarias antes de implementación.

```text
Actua como el Skill architecture-decision
(.github/skills/architecture-decision/SKILL.md).

Entrada: spec aprobada del paso 07.
Salida: impacto, componentes, contratos protegidos, estrategia incremental,
pruebas necesarias, riesgos/trade-offs y decisiones abiertas.

Detente para revision humana antes de implementar.
```

**Salida esperada:** plan técnico incremental y testeable (sin reescrituras ni cambios fuera de alcance).

### 09. Implementation - Implementar un issue aprobado con evidencia

**Tiempo:** 15-20 minutos.

Usa `issue-implementation` para guiar la implementación incremental del Issue aprobado, con pruebas y PR auditable.

```text
Actua como el Skill issue-implementation
(.github/skills/issue-implementation/SKILL.md).

Expediente aprobado (no lo reinterpretes, impleméntalo):
- Issue: [pega título + evidencia + impacto del issue]
- Spec: [pega la spec del paso 07 o su ruta si está en archivo]
- Arquitectura: [pega estrategia + pruebas del paso 08]

Implementa el cambio minimo necesario, ejecuta pruebas relevantes y prepara
un PR con evidencia real.
```

**Salida esperada:** implementación acotada + evidencia de pruebas/validaciones, lista para PR.

### 10. Review - Evaluar el cambio con DoD de ReqFlow

**Tiempo:** 8-10 minutos.

Usa `reqflow-definition-of-done` como evaluator final basado en evidencia. No aprueba por ausencia de señales: exige evidencia concreta.

```text
Actua como el Skill reqflow-definition-of-done
(.github/skills/reqflow-definition-of-done/SKILL.md).

Cambio a evaluar: [diff o ruta del PR del paso 09]
Issue: issue + Spec y arquitectura aprobadas (rutas o texto).
Evidencia disponible: [salida de tests, archivos cambiados].

Para cada criterio responde solo con:
- CUMPLIDO (citar evidencia)
- FALTA EVIDENCIA (decir que falta)
- BLOQUEADO (explicar causa)
- NO APLICA AL ALCANCE (justificar)
- PENDIENTE DE OTRO GATE (indicar cual)

No inventes ejecuciones de CI ni cobertura.
```

**Salida esperada:** una evaluación DoD con evidencia/citas y una decisión explícita de si el cambio puede avanzar a PR.

### 11. Versionar el laboratorio

**Tiempo:** 5 minutos.

Sube todo lo trabajado en S2 (Skills instalados, spec/decisiones/implementación/evaluación y evidencia) y marca el laboratorio con un tag.

```bash
# Desde reqflow-workspace/, en cada repo que cambiaste
cd workshop-auth-backend
git add -A
git commit -m "lab02-s2: ciclo SDLC HU-01"
git push origin HEAD
git tag lab02-s2
git push origin lab02-s2
cd ../workshop-login-frontend
# repite con "lab02-s2: ciclo SDLC HU-05"
```

**Criterio de salida:** cada repo remoto contiene los 5 Skills base instalados (`discovery-analysis`, `spec-writing`, `architecture-decision`, `issue-implementation`, `reqflow-definition-of-done`) junto al Skill de S1, y el tag `lab02-s2` apunta al commit final del laboratorio.

## Qué obtengo

- Repositorio registrado en `subscribers.json` del catálogo, con `.github/workflows/sync-skills.yml` instalado.
- `.github/skills/` con los 5 Skills base de ReqFlow (los mismos usados en el Día 3) junto al de S1.
- Evidencia de un ciclo gobernado: Discovery → Spec → Architecture → Implementation → DoD.
- Commit y tag `lab02-s2` con todo el laboratorio versionado.
