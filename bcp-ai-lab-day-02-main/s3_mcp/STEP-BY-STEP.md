# Laboratorio S3 - MCP con permisos explícitos

**Horario:** 14:00 - 15:20 (1 h 20)
**Objetivo:** Exponer recursos de GitHub a través de MCP (Model Context Protocol) con permisos, logs y decisión humana explícitos, comparando un servidor local con el servidor oficial de GitHub.

## Introducción

Este módulo introduce Model Context Protocol como mecanismo estandarizado para conectar un host que ejecuta un modelo con servidores que exponen contexto y capacidades externas.

La idea central del Día 2 es deliberadamente simple:

```text
Modelo -> MCP -> GitHub
```

Todavía no existe una capa de Custom Agents ni Skills. Esa composición se introducirá después.

## Arquitectura conceptual

```text
+---------------------------+
| VS Code + GitHub Copilot  |  Host
|                           |
|  Modelo                   |
|    |                      |
|  Cliente MCP              |
+----|----------------------+
     |
     | MCP
     v
+---------------------------+
| Servidor MCP              |
| - tools                   |
| - resources               |
| - prompts                 |
+-------------|-------------+
              |
              | API / sistema externo
              v
           GitHub
```

### Host

Es la aplicación donde ocurre la interacción con el modelo. En este laboratorio el host será VS Code con GitHub Copilot.

### Cliente MCP

Es el componente dentro del host que establece y mantiene la conexión MCP con uno o más servidores.

### Servidor MCP

Publica capacidades mediante el protocolo. Un servidor puede exponer tools, resources y prompts, y puede aplicar sus propios límites además de los permisos del sistema externo al que accede.

## Dos escenarios del laboratorio

### Laboratorio 1 - MCP local

```text
VS Code
  |
  | HTTP/MCP
  v
mcp-proxy
  |
  | stdio
  v
mcp-github-project-manager
  |
  | GitHub API
  v
GitHub
```

Este escenario permite ver claramente que el transporte y el servidor son piezas separadas. El servidor original utiliza stdio y el laboratorio agrega una capa HTTP.

### Laboratorio 2 - GitHub MCP oficial

```text
VS Code
  |
  | HTTP/MCP
  v
GitHub MCP Server remoto
  |
  v
GitHub
```

Aquí ya no mantenemos el servidor. Consumimos el MCP oficial de GitHub y observamos cómo cambian autenticación, toolsets, permisos y operación.

## Qué debe quedar claro

Un modelo no obtiene acceso a GitHub por sí mismo. El acceso efectivo depende de varias capas:

```text
intención del usuario
      |
      v
tool disponible en MCP
      |
      v
configuración del servidor
      |
      v
credencial y scopes
      |
      v
permisos reales en GitHub
```

Por eso una tool puede existir y aun así una operación puede ser denegada.

## Resultado esperado

Al terminar el módulo, el participante podrá explicar:

- qué papel cumplen host, cliente y servidor;
- cómo se descubren y usan tools/resources/prompts;
- cómo el contexto llega al modelo;
- qué diferencia hay entre stdio y HTTP;
- cómo se conectan MCP y GitHub;
- por qué las capacidades visibles no equivalen automáticamente a permisos efectivos;
- qué cambia entre un servidor MCP local y el GitHub MCP oficial.

## Materiales

- GitHub CLI autenticado y acceso a un repositorio de laboratorio.
- Podman y PowerShell para levantar el MCP local.
- VS Code con Copilot Chat en modo Agent.
- Repositorio de práctica donde crear `.vscode/mcp.json`.
- No uses repositorios productivos ni muestres tokens en capturas.

Verifica las herramientas antes de empezar:

```bash
git --version
gh --version
podman --version
$PSVersionTable.PSVersion
gh auth status
```

> Si GitHub Projects requiere permisos adicionales, ejecuta `gh auth refresh -s project`. Los permisos efectivos dependen de la cuenta, los scopes, la organización y el repositorio: un scope insuficiente en el token bloquea la acción aunque la tool MCP exista.

## Paso 1 - Levantar el servidor MCP local

**Tiempo:** 20-30 minutos  
**Salida:** servidor MCP disponible en `http://localhost:8081/mcp`.

### Objetivo

Preparar el servidor MCP local y entender cómo un servidor basado en `stdio` puede exponerse mediante HTTP para que VS Code se conecte posteriormente como host/cliente MCP.

En este paso no se configuran Custom Agents ni Skills.

### Arquitectura

```text
GitHub
  ^
  | GitHub API
  |
mcp-github-project-manager
  ^
  | stdio
  |
mcp-proxy
  ^
  | HTTP / MCP
  |
http://localhost:8081/mcp
```

El servidor `mcp-github-project-manager` trabaja originalmente mediante `stdio`. Para este laboratorio se reutiliza dentro de una segunda imagen que agrega `mcp-proxy` y publica un endpoint HTTP.

### Qué capacidades vamos a observar

En este laboratorio no asumiremos que el servidor implementa todas las primitivas MCP posibles.

Trabajaremos con las capacidades que `mcp-github-project-manager` anuncie realmente al cliente, con foco en:

- tools disponibles;
- contexto obtenido a partir de sus resultados;
- transporte;
- autenticación;
- permisos y operaciones denegadas.

Si el servidor no anuncia `resources` o `prompts`, no se simularán ni se reinterpretarán resultados de tools como si lo fueran. Esas capacidades se revisarán de nuevo en el laboratorio del GitHub MCP oficial.

### Prerrequisitos

Comprueba:

```powershell
git --version
gh --version
podman --version
$PSVersionTable.PSVersion
```

Necesitas además acceso a un repositorio GitHub de laboratorio sobre el que conozcas tus permisos.

### Archivos del laboratorio

```text
tools/
`-- mcp-local/
    |-- compose.yaml
    |-- Dockerfile
    `-- start-mcp.ps1
```

### 1.1 Construir el servidor MCP base

El `Dockerfile` parte de:

```dockerfile
FROM localhost/mcp-github-project-manager:latest
```

Por ello, construye primero la imagen base desde el proyecto original:

```powershell
git clone https://github.com/kunwarVivek/mcp-github-project-manager.git
cd mcp-github-project-manager
podman build -t localhost/mcp-github-project-manager:latest .
```

Comprueba:

```powershell
podman images localhost/mcp-github-project-manager
```

### 1.2 Revisar el wrapper HTTP

En `tools/mcp-local/Dockerfile` el laboratorio agrega `mcp-proxy` para transformar el transporte:

```text
stdio -> HTTP
```

El servidor MCP sigue siendo `mcp-github-project-manager`; el proxy solo cambia cómo se expone al cliente.

### 1.3 Revisar `compose.yaml`

El compose pasa al contenedor:

```text
GITHUB_TOKEN
GITHUB_OWNER
GITHUB_REPO
```

y publica el puerto `8081` del host (mapeado al `8080` del contenedor).

No copies tokens directamente en el YAML.

La variable:

```text
AGENT_RECLAIM_ENABLED=false
```

desactiva una función interna de orquestación del propio servidor MCP. No activa ni configura Custom Agents de VS Code.

### 1.4 Preparar autenticación GitHub

Confirma la sesión:

```powershell
gh auth status
```

Si necesitas autenticar:

```powershell
gh auth login
```

Si las operaciones del laboratorio utilizan GitHub Projects y tu entorno requiere el scope correspondiente:

```powershell
gh auth refresh -s project
```

Los permisos efectivos seguirán dependiendo de la cuenta, scopes, organización y repositorio.

### 1.5 Levantar el MCP

Desde:

```text
tools/mcp-local/
```

ejecuta:

```powershell
./start-mcp.ps1 -Owner "TU_OWNER" -Repo "TU_REPO_DE_PRUEBA"
```

El script obtiene el token mediante `gh auth token`, define owner/repo y levanta el servicio con Podman Compose.

### 1.6 Comprobar el endpoint

En otra consola PowerShell:

```powershell
curl.exe -i http://localhost:8081/mcp
```

Antes de que exista una sesión MCP, una respuesta `400 Bad Request` o similar indicando ausencia de `sessionId` puede ser válida: demuestra que el endpoint HTTP existe pero todavía no hay un cliente MCP inicializado.

Comprueba también:

```powershell
podman ps
```

### Qué estamos demostrando

Hasta aquí todavía no interviene ningún Agent personalizado. La arquitectura es simplemente:

```text
proceso MCP stdio
      +
proxy HTTP
      +
credencial GitHub
```

VS Code se conectará en el Paso 2.

### Criterio de salida

- existe la imagen base;
- el wrapper HTTP puede construirse;
- el contenedor está en ejecución;
- el puerto 8081 está publicado;
- `http://localhost:8081/mcp` responde;
- no se configuró ningún Custom Agent ni Skill;
- todavía no se presupone la existencia de `resources` o `prompts` en este servidor.

### Troubleshooting

#### Imagen base no encontrada

```powershell
podman build -t localhost/mcp-github-project-manager:latest .
```

#### Error de autenticación

```powershell
gh auth status
```

#### Puerto 8081 ocupado

```powershell
podman ps
```

Detén el proceso o contenedor anterior antes de levantar nuevamente el laboratorio.

## Paso 2 - Conectar VS Code al MCP local

**Salida:** VS Code conectado al servidor `github-local`, con tools MCP visibles y utilizables desde Copilot Chat en modo Agent, sin usar Custom Agents ni Skills.

### Objetivo

Conectar VS Code al MCP local levantado en el Paso 1 y comprobar que el modelo puede descubrir e invocar capacidades MCP.

> **Importante:** en VS Code, las tools MCP se utilizan desde el modo Agent de Copilot Chat. Esto no significa usar un Custom Agent. En este laboratorio se usa únicamente el modo Agent estándar de VS Code; no se crean ni seleccionan archivos `.agent.md`.

### 2.1 Crear `.vscode/mcp.json`

En la raíz de `reqflow-workspace/` (no dentro de un repo) crea:

```json
{
  "servers": {
    "github-local": {
      "type": "http",
      "url": "http://localhost:8081/mcp"
    }
  }
}
```

Este archivo pertenece a la raíz de `reqflow-workspace/` (ahí lo exigen `check_handoff.py --day 2` y el Día 3), no a este repositorio de material.

### 2.2 Comprobar el servidor y aislar sus tools

1. Abre Copilot Chat.
2. Selecciona Agent en el selector de modo del chat.
3. Abre Configure Tools.
4. Localiza el grupo correspondiente al servidor MCP local. Según la versión de VS Code puede mostrarse con el nombre lógico `github-local` o con un nombre derivado del servidor/proyecto, por ejemplo `github-project-manager_http-local`.
5. Comprueba que sus tools estén visibles y habilitadas.
6. Verifica específicamente que estén disponibles `discover_tools` y `manage_issues`.

Para esta primera prueba conviene reducir la ambigüedad del modelo. Deshabilita temporalmente las tools Built-in que puedan resolver la solicitud por caminos alternativos:

- `agent`;
- `browser`;
- `edit`;
- `execute`;
- `search`;
- `todo`;
- `vscode`;
- `web`.

Mantén habilitada la tool Built-in:

- `read`.

Deja habilitadas también las tools del servidor MCP local.

La razón para mantener `read` es práctica: si el resultado devuelto por una tool MCP es grande, VS Code puede almacenarlo temporalmente en un archivo de sesión y utilizar `read` para procesarlo. En ese caso, `read` no obtiene los datos desde GitHub; únicamente lee el resultado que ya fue obtenido mediante MCP.

El objetivo es observar de forma inequívoca una llamada al MCP local como origen de los datos.

> Si dejas muchas tools habilitadas, el modelo puede decidir utilizar terminal, buscar archivos locales, navegar por la web o elegir otra integración. Eso no demuestra un fallo del MCP; demuestra que el host tenía varias herramientas posibles para resolver la solicitud.

### 2.3 Probar una capacidad real del MCP local

`mcp-github-project-manager` utiliza compound tools: una misma tool agrupa varias operaciones y la operación concreta se selecciona mediante un parámetro `action`.

Para este laboratorio no vamos a profundizar en todas las particularidades internas del servidor local. Solo necesitamos demostrar que:

```text
Copilot Chat
  -> descubre una tool MCP
  -> la invoca con parámetros
  -> el MCP consulta GitHub
  -> el resultado vuelve al modelo
```

Los repositorios de laboratorio normalmente aún no tienen issues: los del backlog (uno por HU) se crean recién en el paso 4. Por eso el orden es: primero creas un issue temporal con una escritura controlada (2.3.2) y después lo lees (2.3.3); así la lectura siempre devuelve datos reales.

#### 2.3.1 Descubrir la capacidad

Inicia una conversación nueva y ejecuta:

```text
Usa exclusivamente la herramienta MCP discover_tools.

Busca qué herramienta y qué acción permiten listar issues de un repositorio.
No uses terminal, archivos locales, web ni ninguna otra herramienta.
```

El resultado esperado es identificar una ruta equivalente a:

```text
manage_issues
  -> action = list
```

#### 2.3.2 Crear un issue temporal (escritura controlada)

Si el servidor y el token lo permiten, solicita una operación inocua en el repositorio de laboratorio. Este issue temporal es el que leerás en la siguiente sección.

Para mantener la prueba determinista, utiliza también la compound tool explícita:

```text
Usa la herramienta MCP manage_issues.

Ejecuta la acción "create" con estos parámetros:

owner: <OWNER>
repo: <REPO>
title: MCP Day 2 - permission test
body: Issue temporal creado durante el laboratorio MCP.

No uses terminal, GitHub CLI, web ni archivos locales.
Antes de ejecutar la operación, muéstrame la tool MCP y los parámetros que vas a utilizar.
```

Antes de autorizar la escritura, revisa la llamada propuesta por VS Code.

No uses repositorios productivos.

#### 2.3.3 Ejecutar una lectura de issues

Ahora que existe al menos un issue (el temporal recién creado), reemplaza `<OWNER>` y `<REPO>` por el repositorio configurado en el Paso 1:

```text
Usa la herramienta MCP manage_issues.

Ejecuta la acción "list" con estos parámetros:

owner: <OWNER>
repo: <REPO>
state: open

No uses terminal, GitHub CLI, web, archivos locales ni ninguna otra herramienta para obtener los datos.

Resume el resultado mostrando número, título y estado de cada issue.
```

Durante la ejecución observa que VS Code muestre una invocación equivalente a:

```text
Ran Manage Issues
Completed with input: {
  "action": "list",
  "owner": "<OWNER>",
  "repo": "<REPO>",
  "state": "open"
}
```

Esa invocación es la evidencia principal de esta sección.

La ruta demostrada es:

```text
Prompt
  -> manage_issues
  -> action = list
  -> parámetros owner/repo/state
  -> servidor MCP
  -> GitHub
  -> resultado estructurado
  -> respuesta del modelo
```

Si VS Code indica que el resultado MCP es grande y lo almacena temporalmente, la tool Built-in `read` puede utilizarse para leer ese archivo y construir el resumen. Esto no cambia el origen de los datos: la consulta a GitHub ya ocurrió mediante `manage_issues`.

> **Nota:** algunas acciones de este servidor local dependen de detalles internos de GitHub GraphQL, como identificadores de nodo. Esas particularidades no forman parte del objetivo de este laboratorio y se dejan fuera del flujo principal. La profundización se hará con el GitHub MCP oficial.

#### 2.3.4 Comparar con un prompt más natural

Una vez demostrado el funcionamiento explícito, inicia una conversación nueva y prueba ahora una solicitud menos técnica:

```text
Usando el MCP local, consulta los issues abiertos de <OWNER>/<REPO> y resume número, título y estado.
```

Observa qué ocurre:

- si el modelo selecciona correctamente `manage_issues`;
- si utiliza antes `discover_tools`;
- si solicita aclaraciones;
- o si no consigue relacionar por sí solo la intención con la compound tool.

Esta comparación permite distinguir entre:

```text
capacidad disponible en el MCP
```

y

```text
capacidad del modelo para seleccionar correctamente esa tool
```

Un fallo de selección de tool no significa necesariamente que el servidor MCP carezca de la operación.

### 2.4 Identificar tools, resultados y contexto

Durante las pruebas distingue:

- el prompt escrito por el usuario;
- la tool MCP seleccionada;
- la `action` utilizada dentro de la compound tool;
- los argumentos enviados al servidor;
- la respuesta devuelta por el servidor;
- el texto final construido por el modelo usando esa información.

En algunas versiones de VS Code, un resultado MCP grande puede almacenarse temporalmente y el host puede utilizar `read` para procesarlo. La evidencia de que los datos se obtuvieron mediante MCP sigue siendo la invocación inicial de la tool MCP y sus argumentos.

La información que el modelo utiliza como contexto puede provenir de resultados de tools o de resources que el servidor publique. No asumas que todos los servidores implementan las mismas primitivas.

### Si Copilot intenta usar terminal o buscar archivos

No continúes con esa ejecución como evidencia del laboratorio.

Comprueba:

1. que el chat esté en modo Agent;
2. que el servidor MCP local esté `Running`;
3. que sus tools aparezcan en Configure Tools;
4. que `discover_tools` y `manage_issues` estén habilitadas;
5. que `read` permanezca habilitada;
6. que las demás tools Built-in indicadas en 2.2 estén deshabilitadas temporalmente;
7. que el prompt incluya `OWNER` y `REPO` explícitos;
8. que, para la primera ejecución, estés nombrando directamente `manage_issues` y la `action` correspondiente.

Después inicia una conversación nueva y repite la prueba.

### Criterio de salida

Debe poder demostrarse que:

- VS Code actúa como host y cliente MCP;
- el servidor MCP local aparece conectado;
- las tools se descubren desde VS Code;
- Copilot Chat está usando el modo Agent estándar, no un Custom Agent;
- `discover_tools` permite identificar una capacidad disponible;
- `manage_issues` puede ejecutarse con `action = list`;
- una consulta real a GitHub llega al modelo a través del servidor MCP;
- `read` puede procesar un resultado MCP grande sin convertirse en la fuente original de los datos;
- puede distinguirse entre disponibilidad de una capacidad y selección automática de la tool por parte del modelo;
- no se utilizó ningún Custom Agent ni Skill.

## Paso 3 - Permisos y límites del MCP local

**Salida:** evidencia de una operación permitida y comprensión de dónde puede aparecer una restricción.

### Objetivo

Comprobar que MCP no reemplaza el modelo de permisos de GitHub.

En este paso no buscamos explorar todas las capacidades del servidor local. Solo queremos demostrar una idea:

```text
tool disponible != operación autorizada
```

Mantén la configuración de tools utilizada al final del Paso 2:

- tools del MCP local habilitadas;
- Built-in `read` habilitada;
- `agent`, `browser`, `edit`, `execute`, `search`, `todo`, `vscode` y `web` deshabilitadas temporalmente.

### 3.1 Revisar el contexto de autenticación

El servidor local recibe `GITHUB_TOKEN`, `GITHUB_OWNER` y `GITHUB_REPO` mediante el script y `compose.yaml` del Paso 1.

Comprueba en PowerShell:

```powershell
gh auth status
```

No muestres el valor del token en capturas o evidencias.

La autorización efectiva depende de varias capas:

```text
tool expuesta por MCP
  -> configuración del servidor
  -> token y scopes
  -> permisos de la cuenta
  -> GitHub
```

### 3.2 Operación de lectura permitida

No utilices un prompt genérico como "consulta los issues del repositorio de laboratorio". Para esta demostración queremos forzar una ruta MCP verificable.

Reemplaza `<OWNER>` y `<REPO>`:

```text
Usa la herramienta MCP manage_issues.

Ejecuta la acción "list" con estos parámetros:

owner: <OWNER>
repo: <REPO>
state: open

No uses terminal, GitHub CLI, web, búsquedas del workspace ni otras herramientas para obtener los datos.

Indica si la operación fue permitida y muestra algunos issues devueltos.
```

La evidencia esperada debe incluir una llamada equivalente a:

```text
Ran Manage Issues
Completed with input: {
  "action": "list",
  "owner": "<OWNER>",
  "repo": "<REPO>",
  "state": "open"
}
```

Si VS Code guarda un resultado grande en un archivo temporal, `read` puede utilizarse para procesarlo. La fuente de los datos sigue siendo la llamada MCP.

### 3.3 Operación de escritura controlada

Solo si tienes permisos de escritura en el repositorio de laboratorio, solicita la creación de un issue temporal:

```text
Usa la herramienta MCP manage_issues.

Ejecuta la acción "create" con estos parámetros:

owner: <OWNER>
repo: <REPO>
title: MCP local - write permission test
body: Issue temporal creado para validar permisos del laboratorio MCP.

No uses terminal, GitHub CLI, web ni archivos del workspace.
Antes de ejecutar, muéstrame la tool MCP y los parámetros que vas a enviar.
```

Antes de autorizar la escritura, revisa la llamada propuesta por VS Code.

Después, cierra o elimina manualmente el issue temporal según las capacidades disponibles.

### 3.4 ¿Dónde puede aparecer una restricción?

No es obligatorio provocar un error artificial si el entorno no ofrece una prueba segura y reproducible.

A partir de las operaciones anteriores, identifica las capas que podrían impedir una ejecución:

```text
A. La tool no existe o no está expuesta por el servidor MCP.
B. La tool existe, pero la configuración del servidor la deshabilita.
C. La tool se invoca, pero el token no tiene el scope necesario.
D. El token es válido, pero la cuenta no tiene permiso sobre el repositorio o recurso.
E. La operación está permitida y GitHub la ejecuta.
```

Si durante el laboratorio aparece de forma natural un error de permisos, úsalo como evidencia y clasifícalo. No modifiques scopes ni permisos únicamente para fabricar un error.

### Qué debe observarse

La parte importante no es memorizar las particularidades de `mcp-github-project-manager`.

Debes poder explicar esta secuencia:

```text
modelo solicita una operación
  -> existe una tool MCP capaz de realizarla
  -> el servidor intenta ejecutarla
  -> GitHub evalúa las credenciales y permisos
  -> la operación se permite o se rechaza
```

El GitHub MCP oficial permitirá profundizar después en controles de exposición y permisos de una implementación mantenida por GitHub.

### Criterio de salida

El participante puede explicar por qué:

```text
tool visible != permiso efectivo
```

y reconoce que una restricción puede producirse en el servidor MCP, su configuración, las credenciales o GitHub.

## Paso 4 - GitHub MCP oficial

**Salida:** VS Code conectado al GitHub MCP oficial, con una comparación práctica frente al MCP local.

### Objetivo

Configurar el servidor MCP oficial de GitHub, probarlo desde VS Code con prompts normales y observar cómo cambian las capacidades, la autenticación y los controles disponibles frente al MCP local.

### 4.1 Servidor remoto oficial

El endpoint remoto oficial es:

```text
https://api.githubcopilot.com/mcp/
```

La configuración exacta de autenticación depende del host y de las políticas de la organización. VS Code puede trabajar con servidores MCP remotos; usa el flujo de autenticación soportado por tu entorno.

Ejemplo base:

```json
{
  "servers": {
    "github-official": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/"
    }
  }
}
```

No incrustes tokens reales directamente en archivos versionados.

### 4.2 Comprobar descubrimiento

Desde VS Code confirma que `github-official` esté conectado y revisa las tools disponibles.

Prompt sugerido:

```text
¿Qué tools MCP tienes disponibles en github-official? No ejecutes ninguna; agrúpalas por propósito.
```

### 4.3 Probar lectura

Para evitar que el modelo intente inferir el repositorio desde el workspace, utiliza siempre el nombre completo en formato `OWNER/REPO`.

Reemplaza `<OWNER>/<REPO>` por el repositorio de laboratorio que estés utilizando:

```text
Usando exclusivamente github-official, consulta los issues abiertos de <OWNER>/<REPO> y resume número, título y estado.

No uses terminal, GitHub CLI, búsquedas del workspace ni archivos locales para obtener los datos.
```

Durante la ejecución observa qué tool del GitHub MCP oficial utiliza VS Code.

Después compara esa tool con la utilizada en el MCP local. El objetivo no es que ambas tengan el mismo nombre, sino comprobar que dos servidores MCP distintos pueden exponer capacidades diferentes para resolver una intención equivalente.

### 4.4 Probar escritura controlada

Si la autenticación y los permisos lo permiten, la escritura no es un issue de prueba: crea **un issue por cada HU del día**, en el repo donde vive cada HU. Estos issues son el backlog que reutilizan los Días 3 y 4.

```text
Usando exclusivamente github-official, crea un issue por cada archivo HU-*.md
de los repos de reqflow-workspace, en el repo donde vive la HU
(<OWNER>/workshop-auth-backend para HU-01, <OWNER>/workshop-login-frontend
para HU-05).

Titulo: el titulo de la HU (por ejemplo "HU-01 - Token firmado con expiracion
y claims minimos").
Cuerpo: la seccion Origen (Id H-xx y evidencia archivo:linea), los Criterios
de aceptacion como checklist y el enlace al PR de S2 si existe.

No uses terminal ni GitHub CLI para realizar la operación.
Antes de ejecutar, muéstrame qué tool MCP vas a utilizar.
```

Crea el Project **ReqFlow** bajo tu owner (una sola vez; los Días 3 y 4 lo reutilizan), agrega cada issue y completa el campo `Hallazgo origen` con el Id `H-xx`:

```powershell
gh project create --owner <OWNER> --title ReqFlow
gh project field-create <NUMERO_PROJECT> --owner <OWNER> --name "Hallazgo origen" --data-type TEXT
gh project item-add <NUMERO_PROJECT> --owner <OWNER> --url <URL_DEL_ISSUE>
```

Si la operación requiere autorización adicional o es rechazada, conserva ese comportamiento como evidencia de permisos y crea los issues desde la interfaz web: el Día 3 los necesita igual.

No uses repositorios productivos.

### 4.5 Toolsets y controles

El GitHub MCP oficial permite configurar conjuntos de capacidades y herramientas individuales. Entre sus controles actuales se incluyen:

- toolsets;
- tools individuales;
- exclusión de tools;
- modo read-only;
- lockdown mode;
- filtrado relacionado con scopes/autenticación.

Cuando no se especifican toolsets, la configuración oficial actual usa por defecto:

```text
context
repos
issues
pull_requests
users
```

#### Ejemplo read-only

Una configuración remota puede solicitar modo solo lectura mediante headers:

```json
{
  "servers": {
    "github-official-readonly": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "X-MCP-Toolsets": "issues,repos,pull_requests",
        "X-MCP-Readonly": "true"
      }
    }
  }
}
```

En este modo las tools de escritura quedan fuera aunque pertenezcan a un toolset solicitado.

#### Comprobación rápida de read-only

No hace falta convertir esta sección en otro laboratorio completo. Basta con dos evidencias:

1. En Configure Tools, comprueba que `github-official-readonly` exponga tools de lectura y que las tools de escritura no estén disponibles.
2. Ejecuta una lectura real sobre `<OWNER>/<REPO>` y confirma que funciona.

Opcionalmente, intenta solicitar una escritura usando exclusivamente `github-official-readonly`:

```text
Usando exclusivamente github-official-readonly, intenta crear un issue en <OWNER>/<REPO>.

Título: MCP readonly test
Cuerpo: Esta operación debería estar bloqueada por read-only.

No uses terminal, GitHub CLI, web ni ninguna otra integración.
Si no existe una tool de escritura disponible, indícalo y no busques otro mecanismo.
```

El comportamiento esperado no tiene por qué ser un error HTTP. La evidencia puede ser simplemente que la tool de escritura no exista dentro de las capacidades expuestas por ese servidor.

#### ¿Read-only es una frontera de seguridad?

No por sí solo.

El archivo `.vscode/mcp.json` está bajo control del usuario o del workspace. Si una persona puede editarlo, también puede eliminar `X-MCP-Readonly` o habilitar otros toolsets. Por ello, esta configuración sirve para reducir la superficie de capacidades del cliente, pero no debe ser la única barrera que proteja una operación sensible.

La autorización efectiva debe entenderse por capas:

```text
VS Code / mcp.json
        |
        v
GitHub MCP Server
        |
        v
OAuth / token scopes
        |
        v
Permisos GitHub sobre el recurso
        |
        v
Rulesets / branch protection / policies
```

Cada capa cumple una función distinta:

| Capa | Alcance |
| --- | --- |
| `mcp.json`, toolsets, exclusiones, read-only | Reduce qué capacidades ofrece el servidor a esa sesión o cliente. |
| OAuth / PAT scopes | Limita qué puede solicitar la identidad autenticada. |
| Permisos del repositorio u organización | Determina qué puede hacer realmente esa identidad sobre el recurso. |
| Rulesets, branch protection y controles similares | Impone reglas adicionales incluso a usuarios que ya tienen permisos de escritura. |
| Policies de organización/enterprise | Gobiernan si determinadas capacidades, como MCP en Copilot, están habilitadas y bajo qué condiciones. |

Regla práctica:

```text
mcp.json
= configuración de capacidad

OAuth / token scopes
= autorización de identidad

GitHub permissions
= autorización sobre el recurso

Rulesets / policies
= gobernanza
```

Por ejemplo, si un usuario cambia `X-MCP-Readonly` de `true` a `false`, pero su identidad solo tiene permisos de lectura sobre el repositorio, no debería obtener capacidad real de escritura. La configuración del MCP puede dejar de restringirlo, pero las capas de autorización de GitHub continúan aplicándose.

En cambio, si la misma identidad ya tiene permisos de escritura y la única restricción era `read-only` en un archivo que ella misma controla, quitar esa opción sí puede volver a exponer tools de escritura.

Por eso la estrategia recomendada es aplicar least privilege y defensa en profundidad:

```text
scopes mínimos
    +
permisos GitHub mínimos necesarios
    +
rulesets/policies
    +
MCP configurado solo con las tools necesarias
```

`mcp.json` ayuda a reducir superficie y errores accidentales; la seguridad real no debe depender únicamente de que ese archivo permanezca sin cambios.

### 4.6 Comparación final

Completa la comparación con evidencia observada en tu entorno:

| Aspecto | MCP local | GitHub MCP oficial |
| --- | --- | --- |
| Quién mantiene el servidor | equipo/proyecto tercero | GitHub |
| Ejecución | local con Podman | remoto oficial |
| Transporte observado | HTTP sobre wrapper de servidor stdio | HTTP remoto |
| Capacidades | las implementadas por `mcp-github-project-manager` | toolsets/tools oficiales GitHub |
| Configuración | variables y configuración del servidor local | toolsets, tools, exclusiones y controles del servidor oficial |
| Autorización final | token + permisos GitHub | autenticación/scopes + permisos GitHub |

### 4.7 Pregunta de cierre

El participante debe poder responder:

> Si el modelo es el mismo, ¿por qué cambian las cosas que puede hacer cuando cambiamos de servidor MCP?

Respuesta esperada: porque las capacidades no pertenecen al modelo. Dependen de las tools/resources expuestas por el servidor, su configuración y los permisos efectivos del sistema externo.

### Criterio de salida

Debe poder demostrarse el flujo:

```text
Modelo -> MCP -> GitHub
```

con dos implementaciones MCP diferentes y sin usar Custom Agents, Skills ni SDD.

## Paso 5 - Versionar el laboratorio

**Tiempo estimado:** 5 minutos.

`reqflow-workspace/` no es un repo git: se versiona **dentro de cada repo que tocaste**. Guarda la evidencia de S3 en `docs/mcp-evidence/` del repo (capturas o transcripciones de `discover_tools`, `Ran Manage Issues`, comparativa local vs oficial) más una **copia** de tu `.vscode/mcp.json` **sin tokens**; el original se queda en la raíz del workspace (lo exigen el gate y el Día 3).

```powershell
# Desde reqflow-workspace/, en cada repo que cambiaste
cd workshop-auth-backend
New-Item -ItemType Directory -Force docs\mcp-evidence
Copy-Item ..\.vscode\mcp.json docs\mcp-evidence\mcp.json
git add -A
git commit -m "lab02-s3: mcp local + github mcp oficial con permisos explicitos"
git push origin HEAD
git tag lab02-s3
git push origin lab02-s3
```

Cierra además el día (igual que el paso 3 del cierre del Día 1), en cada repo que cambiaste:

```powershell
# Estando ya en el repo (p. ej. workshop-auth-backend)
git tag day2-done
git push --follow-tags
```

**Criterio de salida:** cada repo remoto que cambiaste contiene `docs/mcp-evidence/` (con la copia de `mcp.json` sin tokens ni secretos), el tag `lab02-s3` apunta al commit final del laboratorio y existe el tag `day2-done`.

## Qué obtengo

- MCP local levantado con Podman y endpoint HTTP accesible.
- Servidor local y GitHub MCP oficial visibles y usados desde VS Code.
- Evidencia de `discover_tools`, consulta real de issues y una prueba de permisos o restricción.
- Validación de lectura con el servidor oficial y su configuración read-only.
- Comparación documentada: mantenimiento, ejecución, transporte, capacidades, configuración y autorización.
- Explicación demostrable del flujo `Modelo -> MCP -> GitHub`, sin Custom Agents, Skills ni SDD.
- Commit y tag `lab02-s3` con todo el laboratorio versionado.

**Criterio de salida general:** el participante distingue entre capacidades expuestas por un servidor MCP, selección de tools por el modelo y autorización efectiva de GitHub.
