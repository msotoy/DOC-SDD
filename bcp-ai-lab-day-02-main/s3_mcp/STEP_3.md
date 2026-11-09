# Paso 3 - Permisos y límites del MCP local

**Salida:** evidencia de una operación permitida y comprensión de dónde puede aparecer una restricción.

## Objetivo

Comprobar que MCP no reemplaza el modelo de permisos de GitHub.

En este paso no buscamos explorar todas las capacidades del servidor local. Solo queremos demostrar una idea:

```text
tool disponible != operación autorizada
```

Mantén la configuración de tools utilizada al final del Paso 2:

- tools del MCP local habilitadas;
- Built-in `read` habilitada;
- `agent`, `browser`, `edit`, `execute`, `search`, `todo`, `vscode` y `web` deshabilitadas temporalmente.

## 3.1 Revisar el contexto de autenticación

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

## 3.2 Operación de lectura permitida

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

## 3.3 Operación de escritura controlada

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

## 3.4 ¿Dónde puede aparecer una restricción?

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

## Qué debe observarse

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

## Criterio de salida

El participante puede explicar por qué:

```text
tool visible != permiso efectivo
```

y reconoce que una restricción puede producirse en el servidor MCP, su configuración, las credenciales o GitHub.
