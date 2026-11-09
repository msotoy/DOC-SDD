# Servidor MCP Local (Model Context Protocol)

**Tiempo estimado:** 5 a 10 minutos  
**Puertos expuestos:** 
* `http://localhost:8083` → Servicio MCP GitHub Projects (8080 queda libre para Quarkus)
* `http://localhost:8081` → Servicio MCP GitHub Tasks / Backlog (**Usado por S1 y S2**)

---

## 1. ¿Qué es este componente y por qué se necesita?

En el **Día 04**, los agentes inteligentes de **S1 (CrewAI)** y **S2 (LangGraph)** no reciben el requerimiento bancario a mano como un texto plano, sino que actúan como un equipo real de desarrollo: **leen el backlog en vivo desde un GitHub Project** a través del protocolo abierto **MCP (Model Context Protocol)**.

Para que esto funcione sin exponer credenciales dentro de los scripts de Python, se levanta este servicio local en contenedor (usando **Podman** o **Docker**) que actúa como puente seguro entre GitHub y los agentes.

```
+-------------------+           +-----------------------+           +-------------------+
|  GitHub Projects  | <=======> |  Servidor MCP Local   | <=======> |  Agentes S1 / S2  |
|  (Issues/Backlog) | (GitHub)  |  (Puerto 8081 HTTP)   |  (HTTP)   |  (CrewAI/LangG.)  |
+-------------------+           +-----------------------+           +-------------------+
```

---

## 2. Prerrequisitos

Antes de iniciar el servicio MCP, verifica que tu entorno tenga:

1. **GitHub CLI (`gh`)**: Instalado y autenticado.
2. **Motor de Contenedores**:
   * **Podman** (Entorno oficial del laboratorio / BCP).
   * **O Docker Desktop** (Soportado automáticamente si estás en máquina personal).
3. **PowerShell 7** o Windows PowerShell.

### Paso previo: Autenticar GitHub CLI con permisos de proyectos
Abre una terminal y ejecuta:

```powershell
# 1. Iniciar sesión en GitHub
gh auth login

# 2. Asegurar que el token tenga permisos para leer Projects
gh auth refresh -s project

# 3. Comprobar que la sesión esté activa
gh auth status
```

---

## 3. Cómo Levantar el Servidor MCP

> ⚠️ **IMPORTANTE:** Esta terminal debe **permanecer abierta** durante todo el laboratorio para que los agentes puedan consultar el backlog.

Abre una terminal de PowerShell dedicada y ejecuta:

### Con Podman (Recomendado en el laboratorio)
```powershell
cd c:\...\bcp-ai-lab-day-04\00_support\mcp-local
.\start-mcp.ps1 -Owner "<OWNER>" -Repo "workshop-requirements-api"
```

### Con Docker (Si estás en tu máquina personal con Docker Desktop)
El script auto-detecta si tienes Docker si no encuentra Podman, o puedes forzarlo con:
```powershell
cd c:\...\bcp-ai-lab-day-04\00_support\mcp-local
.\start-mcp.ps1 -Owner "<OWNER>" -Repo "workshop-requirements-api" -Engine docker
```

---

## 4. ¿Qué hace `start-mcp.ps1` internamente?

1. Detecta si estás usando **Podman** o **Docker**.
2. Obtiene automáticamente tu token seguro ejecutando `gh auth token`.
3. Exporta las variables de entorno necesarias (`GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO`).
4. Construye las imágenes necesarias usando `Dockerfile` (con `mcp-proxy` como `ENTRYPOINT`).
5. Levanta los dos servicios definidos en `compose.yaml` (run-only, `--in-pod false`):
   * **`github-project`** en `http://localhost:8083`
   * **`github-task`** en `http://localhost:8081` (este es el puerto configurado en `s1_crewai/.env` y `s2_langgraph/.env`).

---

## 5. Verificación de Funcionamiento

Para confirmar que el servicio está respondiendo correctamente sin cerrar la terminal del MCP, abre otra consola PowerShell y corre:

```powershell
curl.exe -i http://localhost:8081/mcp
```

*Respuesta esperada:* Una respuesta HTTP `400 Bad Request` con el mensaje `No sessionId`.  
✅ **Esto es completamente normal y correcto:** significa que el servidor MCP está vivo, escuchando y esperando la conexión de los agentes con una sesión inicializada.

Una vez que veas esto, ya puedes pasar a ejecutar **S1 (CrewAI)** o **S2 (LangGraph)**.
