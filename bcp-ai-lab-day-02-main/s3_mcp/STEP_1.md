# Paso 1 - Levantar el servidor MCP local

**Tiempo:** 20-30 minutos  
**Salida:** servidor MCP disponible en `http://localhost:8081/mcp`.

## Objetivo

Preparar el servidor MCP local y entender cómo un servidor basado en `stdio` puede exponerse mediante HTTP para que VS Code se conecte posteriormente como host/cliente MCP.

En este paso no se configuran Custom Agents ni Skills.

## Arquitectura

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

## Qué capacidades vamos a observar

En este laboratorio no asumiremos que el servidor implementa todas las primitivas MCP posibles.

Trabajaremos con las capacidades que `mcp-github-project-manager` anuncie realmente al cliente, con foco en:

- tools disponibles;
- contexto obtenido a partir de sus resultados;
- transporte;
- autenticación;
- permisos y operaciones denegadas.

Si el servidor no anuncia `resources` o `prompts`, no se simularán ni se reinterpretarán resultados de tools como si lo fueran. Esas capacidades se revisarán de nuevo en el laboratorio del GitHub MCP oficial.

## Prerrequisitos

Comprueba:

```powershell
git --version
gh --version
podman --version
$PSVersionTable.PSVersion
```

Necesitas además acceso a un repositorio GitHub de laboratorio sobre el que conozcas tus permisos.

## Archivos del laboratorio

```text
tools/
`-- mcp-local/
    |-- compose.yaml
    |-- Dockerfile
    `-- start-mcp.ps1
```

## 1.1 Construir el servidor MCP base

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

## 1.2 Revisar el wrapper HTTP

En `tools/mcp-local/Dockerfile` el laboratorio agrega `mcp-proxy` para transformar el transporte:

```text
stdio -> HTTP
```

El servidor MCP sigue siendo `mcp-github-project-manager`; el proxy solo cambia cómo se expone al cliente.

## 1.3 Revisar `compose.yaml`

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

## 1.4 Preparar autenticación GitHub

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

## 1.5 Levantar el MCP

Desde:

```text
tools/mcp-local/
```

ejecuta:

```powershell
./start-mcp.ps1 -Owner "TU_OWNER" -Repo "TU_REPO_DE_PRUEBA"
```

El script obtiene el token mediante `gh auth token`, define owner/repo y levanta el servicio con Podman Compose.

## 1.6 Comprobar el endpoint

En otra consola PowerShell:

```powershell
curl.exe -i http://localhost:8081/mcp
```

Antes de que exista una sesión MCP, una respuesta `400 Bad Request` o similar indicando ausencia de `sessionId` puede ser válida: demuestra que el endpoint HTTP existe pero todavía no hay un cliente MCP inicializado.

Comprueba también:

```powershell
podman ps
```

## Qué estamos demostrando

Hasta aquí todavía no interviene ningún Agent personalizado. La arquitectura es simplemente:

```text
proceso MCP stdio
      +
proxy HTTP
      +
credencial GitHub
```

VS Code se conectará en el Paso 2.

## Criterio de salida

- existe la imagen base;
- el wrapper HTTP puede construirse;
- el contenedor está en ejecución;
- el puerto 8081 está publicado;
- `http://localhost:8081/mcp` responde;
- no se configuró ningún Custom Agent ni Skill;
- todavía no se presupone la existencia de `resources` o `prompts` en este servidor.

## Troubleshooting

### Imagen base no encontrada

```powershell
podman build -t localhost/mcp-github-project-manager:latest .
```

### Error de autenticación

```powershell
gh auth status
```

### Puerto 8081 ocupado

```powershell
podman ps
```

Detén el proceso o contenedor anterior antes de levantar nuevamente el laboratorio.
