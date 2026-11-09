# Protocolo MCP (Model Context Protocol) en Entornos Bancarios

> **Módulo de Referencia Técnica · BCP AI Lab (Día 04)**  
> *Alineado con el servicio local `00_support/mcp-local` y los clientes `mcp_projects.py` y `mcp_git.py`.*

---

## 1. ¿Qué es MCP y por qué se usa en este laboratorio?

En sistemas multi-agente empresariales, los agentes no deben recibir credenciales sensibles de bases de datos ni tokens de GitHub directamente dentro del código Python.

El **Model Context Protocol (MCP)** es un estándar abierto que actúa como middleware seguro entre los modelos de lenguaje (LLMs) y los recursos externos:
* Los agentes descubren herramientas en runtime (`tools/list`).
* Las llamadas a herramientas (`tools/call`) se realizan mediante un protocolo estandarizado sobre **JSON-RPC 2.0**.
* La autenticación con GitHub se delega a un contenedor local seguro que inyecta los tokens automáticamente.

```text
+-------------------+           +-----------------------+           +-------------------+
|  GitHub Projects  | <=======> |  Servidor MCP Local   | <=======> |  Agentes S1 / S2  |
|  (Issues/Backlog) |  GitHub   |  (Puerto 8081 HTTP)   |  HTTP/RPC |  (CrewAI/LangG.)  |
+-------------------+           +-----------------------+           +-------------------+
```

---

## 2. Puertos y Servicios del Laboratorio

El archivo `00_support/mcp-local/compose.yaml` levanta dos servicios de forma simultánea:

| Puerto | Servicio | Rol en el Laboratorio |
| :--- | :--- | :--- |
| **`8083`** | `github-project` | Gestión de proyectos de alto nivel en GitHub Projects. |
| **`8081`** | `github-task` | **Backlog y Tareas:** Usado directamente por **S1 (CrewAI)** y **S2 (LangGraph)** para leer historias de usuario y criterios de aceptación. |
| **`8082`** | `mcp-git` | **Operaciones Git:** Usado por **S3 (Harness)** para abrir Pull Requests de forma programática. |

---

## 3. Despliegue con Podman o Docker (`start-mcp.ps1`)

El script de arranque ubicado en `00_support/mcp-local/start-mcp.ps1` detecta automáticamente el motor de contenedores de tu máquina:

```powershell
cd 00_support\mcp-local

# Modo oficial (Podman en entornos BCP/NTT DATA):
.\start-mcp.ps1 -Owner "<OWNER>" -Repo "workshop-requirements-api"

# Modo Docker Desktop (en máquinas personales):
.\start-mcp.ps1 -Owner "<OWNER>" -Repo "workshop-requirements-api" -Engine docker
```

### ¿Qué hace el script internamente?
1. Ejecuta `gh auth token` para obtener las credenciales de GitHub sin escribirlas en disco.
2. Inyecta `GITHUB_OWNER`, `GITHUB_REPO` y `GITHUB_TOKEN` en variables de entorno temporales.
3. Compila `Dockerfile` (imagen run-only con `mcp-proxy` como `ENTRYPOINT`) e inicia el proxy, exponiendo el transporte `stdio` mediante HTTP. El compose solo levanta (`image:` + `--in-pod false`, sin `build:`).

---

## 4. Transporte Streamable HTTP sobre `/mcp`

El cliente Python implementado en `mcp_projects.py` no utiliza WebSockets ni endpoints `/sse` separados; utiliza **Streamable HTTP**:

```text
POST http://localhost:8081/mcp
Headers:
  Content-Type: application/json
  Accept: application/json, text/event-stream
Body:
  {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {...}}
```

### Handshake y Ciclo de Vida:
1. **Handshake `initialize`:** El cliente envía `initialize` y recibe en los encabezados HTTP el identificador de sesión `Mcp-Session-Id`.
2. **Notificación `notifications/initialized`:** Confirma que el cliente está listo para operar.
3. **Persistencia de Sesión:** En todas las peticiones posteriores, el cliente envía el header `Mcp-Session-Id: <id>`.

### Detección de Errores en Tools (`isError: true`):
En el protocolo MCP, cuando una tool falla (por ejemplo, si un issue no existe), la llamada HTTP responde con código `200 OK`, pero incluye dentro del payload JSON:
```json
{
  "content": [{"type": "text", "text": "Issue #999 not found"}],
  "isError": true
}
```
El helper `call_tool()` de `mcp_projects.py` inspecciona activamente la bandera `isError`. Si es `true`, levanta una excepción `RuntimeError` en Python para activar los fallbacks correspondientes.

---

## 5. Inspección Visual con MCP Inspector

Para auditar y probar las herramientas del MCP antes de ejecutar el pipeline de IA, puedes usar el Inspector oficial:

```powershell
npx @modelcontextprotocol/inspector
```

1. Abre `http://localhost:5173` en tu navegador.
2. Conéctate a `http://localhost:8081/mcp` usando transporte **Streamable HTTP**.
3. Podrás inspeccionar la lista de herramientas (`tools/list`), ver los esquemas JSON de entrada y probar llamadas a `manage_project` o `manage_issues` en tiempo real.
