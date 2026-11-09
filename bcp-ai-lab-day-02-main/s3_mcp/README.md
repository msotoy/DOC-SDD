# S3 - Model Context Protocol (MCP)

Este módulo está dedicado exclusivamente a **Model Context Protocol (MCP)**.

No se utilizan Custom Agents, Agent Skills ni Spec Driven Development. Todas las pruebas se realizan desde VS Code + GitHub Copilot Chat con prompts normales.

## Objetivo

Comprender cómo un modelo puede descubrir contexto y capacidades externas mediante MCP y aplicarlo primero con un servidor MCP local y después con el servidor MCP oficial de GitHub.

Al finalizar, el participante debe poder explicar y demostrar este flujo:

```text
Modelo -> MCP -> GitHub
```

## Ruta del módulo

1. [Introducción](INTRODUCTION.md) - conceptos y arquitectura.
2. [Teoría MCP](THEORY.md) - host, cliente, servidor, tools, resources, prompts, permisos y transportes.
3. [Paso 1](STEP_1.md) - levantar el MCP local y exponerlo por HTTP.
4. [Paso 2](STEP_2.md) - conectar VS Code y probar tools/contexto con prompts normales.
5. [Paso 3](STEP_3.md) - comprobar permisos, límites y operaciones permitidas/denegadas.
6. [Paso 4](STEP_4.md) - configurar y probar el GitHub MCP oficial.
7. [Guía paso a paso](STEP-BY-STEP.md) - índice y criterios de salida.

## Alcance

### Incluido

- fundamentos MCP;
- host, cliente y servidor;
- tools, resources y prompts;
- contexto aportado mediante MCP;
- stdio y HTTP;
- MCP local con Podman;
- integración MCP con VS Code;
- permisos y límites;
- GitHub MCP oficial;
- comparación entre MCP local y GitHub MCP.

### Fuera de alcance

- Custom Agents;
- Agent Skills;
- SDD;
- roles PM/PO, Architect, Bootstrap o Developer;
- automatización agentic de backlog o implementación.

Esos temas se cubren en el Día 3 (`bcp-ai-lab-day-03`), no en este módulo.

## Requisitos

- Windows;
- PowerShell 7;
- Git;
- GitHub CLI (`gh`);
- Podman;
- VS Code;
- GitHub Copilot habilitado;
- un repositorio GitHub de prueba sobre el que el participante tenga permisos conocidos.

## Regla de seguridad

Usar únicamente repositorios de laboratorio. No utilizar tokens, secretos, datos ni repositorios productivos.
