# Teoría - Model Context Protocol

## ¿Qué es MCP?

Model Context Protocol (MCP) es un protocolo abierto para que aplicaciones que trabajan con modelos se conecten de forma estructurada con fuentes de contexto y capacidades externas.

MCP no reemplaza al modelo, ni a GitHub, ni a las APIs existentes. Define una forma común de describir, descubrir e invocar capacidades.

## Host, cliente y servidor

- **Host:** aplicación que contiene la experiencia del usuario y coordina al modelo. En este laboratorio: VS Code + GitHub Copilot.
- **Cliente MCP:** componente del host que establece la sesión con un servidor MCP.
- **Servidor MCP:** proceso local o remoto que ofrece capacidades MCP.

Un host puede conectarse a más de un servidor MCP.

## Tools

Las tools representan acciones que el modelo puede solicitar al servidor, por ejemplo consultar issues, crear un issue o leer datos de un repositorio.

Una tool disponible no implica permiso efectivo. La ejecución también depende de la configuración del servidor, credenciales, scopes y autorización del sistema final.

## Resources

Los resources permiten al servidor ofrecer información identificable que el host puede incorporar al contexto del modelo.

El servidor decide qué resources publica y el cliente decide cómo utilizarlos dentro de la interacción.

> **Importante:** MCP define varias primitivas, pero un servidor concreto no está obligado a implementar todas. Durante el laboratorio siempre se trabajará con las capacidades que el servidor realmente anuncie. No se interpretará la salida de una tool como si fuera un resource.

## Prompts

MCP también contempla prompts publicados por el servidor: plantillas reutilizables que el host puede presentar o utilizar.

En este Día 2 no construiremos una estrategia de prompts ni Skills alrededor de ellos; solo reconoceremos que forman parte del protocolo.

## ¿Y el "context"?

Es importante distinguir conceptos:

```text
Tools      -> acciones/capacidades
Resources  -> información accesible
Prompts    -> plantillas proporcionadas por el servidor
Contexto   -> información que finalmente llega al modelo durante la interacción
```

Por tanto, "context" no debe enseñarse como si fuera simplemente una cuarta primitiva equivalente a tools/resources/prompts.

El contexto puede provenir de diferentes fuentes: archivos del workspace, conversación, respuestas de tools, resources MCP u otras capacidades del host.

## Permisos y límites

El acceso efectivo es la intersección de varias capas:

```text
capacidad implementada por el servidor
AND
capacidad habilitada por configuración
AND
scope de la credencial
AND
permiso del usuario/token sobre GitHub
AND
restricciones propias del recurso
```

Esto permite demostrar tres situaciones distintas:

1. una tool no está publicada;
2. la tool está publicada pero está deshabilitada por configuración;
3. la tool está disponible, pero GitHub rechaza la operación por permisos.

## Transporte

MCP puede operar con distintos transportes. Para este laboratorio interesan especialmente:

### stdio

El host lanza o se comunica con un proceso local mediante entrada/salida estándar.

Ventajas:

- simple para servidores locales;
- no requiere publicar un puerto;
- el ciclo de vida puede quedar ligado al host.

### HTTP

El servidor se expone mediante una dirección HTTP MCP.

Ventajas:

- desacopla cliente y proceso servidor;
- permite servidores remotos;
- resulta útil para demostrar un endpoint independiente del host.

En el Laboratorio 1 veremos ambos a la vez: el servidor local original trabaja por stdio y `mcp-proxy` lo expone por HTTP.

## Qué demostrará cada laboratorio

### Laboratorio 1 - MCP local

Con `mcp-github-project-manager` se demostrarán las capacidades que realmente publique el servidor, con foco en:

- descubrimiento e invocación de tools;
- transporte `stdio -> HTTP`;
- contexto obtenido a partir de resultados MCP;
- autenticación, permisos y operaciones denegadas.

Si durante la sesión este servidor no anuncia `resources` o `prompts`, se registrará como una característica de esa implementación, no como una carencia del protocolo.

### Laboratorio 2 - GitHub MCP oficial

El segundo laboratorio permitirá comparar el servidor local con la implementación oficial de GitHub y revisar con más detalle las capacidades que el servidor oficial anuncie en ese momento.

La guía no presupone que todas las primitivas estén disponibles: primero se inspeccionarán las capacidades anunciadas y luego se probarán únicamente las que estén realmente habilitadas.

## MCP local vs GitHub MCP oficial

### MCP local del laboratorio

- se construye y ejecuta en nuestra máquina;
- usa Podman;
- depende de un servidor de terceros (`mcp-github-project-manager`);
- se expone por HTTP mediante `mcp-proxy`;
- nosotros controlamos su proceso y configuración;
- sus capacidades son únicamente las que ese proyecto implemente y anuncie.

### GitHub MCP oficial

- es mantenido por GitHub;
- puede consumirse como servidor remoto oficial;
- ofrece capacidades propias de GitHub;
- admite controles como selección de toolsets, exclusión de tools y modo read-only;
- la autenticación y los scopes siguen determinando qué operaciones son realmente posibles.

## Regla mental del Día 2

```text
Modelo
  |
  v
MCP
  |
  v
GitHub
```

El Día 3 agregará nuevas capas de especialización sobre esta base, pero MCP debe entenderse primero de forma independiente.
