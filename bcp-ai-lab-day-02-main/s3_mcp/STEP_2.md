# Paso 2 - Conectar VS Code al MCP local

**Salida:** VS Code conectado al servidor `github-local`, con tools MCP visibles y utilizables desde Copilot Chat en modo Agent, sin usar Custom Agents ni Skills.

## Objetivo

Conectar VS Code al MCP local levantado en el Paso 1 y comprobar que el modelo puede descubrir e invocar capacidades MCP.

> **Importante:** en VS Code, las tools MCP se utilizan desde el modo **Agent** de Copilot Chat. Esto no significa usar un **Custom Agent**. En este laboratorio se usa únicamente el modo Agent estándar de VS Code; no se crean ni seleccionan archivos `.agent.md`.

## 2.1 Crear `.vscode/mcp.json`

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

## 2.2 Comprobar el servidor y aislar sus tools

1. Abre Copilot Chat.
2. Selecciona **Agent** en el selector de modo del chat.
3. Abre **Configure Tools**.
4. Localiza el grupo correspondiente al servidor MCP local. Según la versión de VS Code puede mostrarse con el nombre lógico `github-local` o con un nombre derivado del servidor/proyecto, por ejemplo `github-project-manager_http-local`.
5. Comprueba que sus tools estén visibles y habilitadas.
6. Verifica específicamente que estén disponibles `discover_tools` y `manage_issues`.

Para esta primera prueba conviene reducir la ambigüedad del modelo. Deshabilita temporalmente las tools **Built-in** que puedan resolver la solicitud por caminos alternativos:

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

El objetivo de esta sección es observar de forma inequívoca una llamada al MCP local como origen de los datos.

> Si dejas muchas tools habilitadas, el modelo puede decidir utilizar terminal, buscar archivos locales, navegar por la web o elegir otra integración. Eso no demuestra un fallo del MCP; demuestra que el host tenía varias herramientas posibles para resolver la solicitud.

## 2.3 Probar una capacidad real del MCP local

`mcp-github-project-manager` utiliza **compound tools**: una misma tool agrupa varias operaciones y la operación concreta se selecciona mediante un parámetro `action`.

Para este laboratorio no vamos a profundizar en todas las particularidades internas del servidor local. Solo necesitamos demostrar que:

```text
Copilot Chat
  -> descubre una tool MCP
  -> la invoca con parámetros
  -> el MCP consulta GitHub
  -> el resultado vuelve al modelo
```

Los repositorios de laboratorio normalmente aún no tienen issues: los del backlog (uno por HU) se crean recién en el paso 4. Por eso el orden es: primero creas un issue temporal con una escritura controlada (2.3.2) y después lo lees (2.3.3); así la lectura siempre devuelve datos reales.

### 2.3.1 Descubrir la capacidad

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

### 2.3.2 Crear un issue temporal (escritura controlada)

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

### 2.3.3 Ejecutar una lectura de issues

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

### 2.3.4 Comparar con un prompt más natural

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

## 2.4 Identificar tools, resultados y contexto

Durante las pruebas distingue:

- el prompt escrito por el usuario;
- la tool MCP seleccionada;
- la `action` utilizada dentro de la compound tool;
- los argumentos enviados al servidor;
- la respuesta devuelta por el servidor;
- el texto final construido por el modelo usando esa información.

En algunas versiones de VS Code, un resultado MCP grande puede almacenarse temporalmente y el host puede utilizar `read` para procesarlo. La evidencia de que los datos se obtuvieron mediante MCP sigue siendo la invocación inicial de la tool MCP y sus argumentos.

La información que el modelo utiliza como contexto puede provenir de resultados de tools o de resources que el servidor publique. No asumas que todos los servidores implementan las mismas primitivas.

## Si Copilot intenta usar terminal o buscar archivos

No continúes con esa ejecución como evidencia del laboratorio.

Comprueba:

1. que el chat esté en modo **Agent**;
2. que el servidor MCP local esté `Running`;
3. que sus tools aparezcan en **Configure Tools**;
4. que `discover_tools` y `manage_issues` estén habilitadas;
5. que `read` permanezca habilitada;
6. que las demás tools Built-in indicadas en 2.2 estén deshabilitadas temporalmente;
7. que el prompt incluya `OWNER` y `REPO` explícitos;
8. que, para la primera ejecución, estés nombrando directamente `manage_issues` y la `action` correspondiente.

Después inicia una conversación nueva y repite la prueba.

## Criterio de salida

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
