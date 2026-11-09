# Introducción a MCP

## Objetivo del módulo

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
