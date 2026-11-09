# Paso 4 - GitHub MCP oficial

**Salida:** VS Code conectado al GitHub MCP oficial, con una comparación práctica frente al MCP local.

## Objetivo

Configurar el servidor MCP oficial de GitHub, probarlo desde VS Code con prompts normales y observar cómo cambian las capacidades, la autenticación y los controles disponibles frente al MCP local.

## 4.1 Servidor remoto oficial

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

## 4.2 Comprobar descubrimiento

Desde VS Code confirma que `github-official` esté conectado y revisa las tools disponibles.

Prompt sugerido:

```text
¿Qué tools MCP tienes disponibles en github-official? No ejecutes ninguna; agrúpalas por propósito.
```

## 4.3 Probar lectura

Para evitar que el modelo intente inferir el repositorio desde el workspace, utiliza siempre el nombre completo en formato `OWNER/REPO`.

Reemplaza `<OWNER>/<REPO>` por el repositorio de laboratorio que estés utilizando:

```text
Usando exclusivamente github-official, consulta los issues abiertos de <OWNER>/<REPO> y resume número, título y estado.

No uses terminal, GitHub CLI, búsquedas del workspace ni archivos locales para obtener los datos.
```

Durante la ejecución observa qué tool del GitHub MCP oficial utiliza VS Code.

Después compara esa tool con la utilizada en el MCP local. El objetivo no es que ambas tengan el mismo nombre, sino comprobar que dos servidores MCP distintos pueden exponer capacidades diferentes para resolver una intención equivalente.

## 4.4 Probar escritura controlada

Si la autenticación y los permisos lo permiten, la escritura no es un issue de prueba: crea **un issue por cada HU del día**, en el repo donde vive cada HU. Estos issues son el backlog que reutilizan los Días 3 y 4.

```text
Usando exclusivamente github-official, crea un issue por cada archivo HU-*.md
de los repos de reqflow-workspace, en el repo donde vive la HU
(<OWNER>/workshop-auth-backend, <OWNER>/workshop-login-frontend).

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

## 4.5 Toolsets y controles

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

### Ejemplo read-only

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

### Comprobación rápida de read-only

No hace falta convertir esta sección en otro laboratorio completo. Basta con dos evidencias:

1. En **Configure Tools**, comprueba que `github-official-readonly` exponga tools de lectura y que las tools de escritura no estén disponibles.
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

### ¿Read-only es una frontera de seguridad?

No por sí solo.

El archivo `.vscode/mcp.json` está bajo control del usuario o del workspace. Si una persona puede editarlo, también puede eliminar `X-MCP-Readonly` o habilitar otros toolsets. Por ello, esta configuración sirve para **reducir la superficie de capacidades del cliente**, pero no debe ser la única barrera que proteja una operación sensible.

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

Por eso la estrategia recomendada es aplicar **least privilege y defensa en profundidad**:

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

## 4.6 Comparación final

Completa la comparación con evidencia observada en tu entorno:

| Aspecto | MCP local | GitHub MCP oficial |
| --- | --- | --- |
| Quién mantiene el servidor | equipo/proyecto tercero | GitHub |
| Ejecución | local con Podman | remoto oficial |
| Transporte observado | HTTP sobre wrapper de servidor stdio | HTTP remoto |
| Capacidades | las implementadas por `mcp-github-project-manager` | toolsets/tools oficiales GitHub |
| Configuración | variables y configuración del servidor local | toolsets, tools, exclusiones y controles del servidor oficial |
| Autorización final | token + permisos GitHub | autenticación/scopes + permisos GitHub |

## 4.7 Pregunta de cierre

El participante debe poder responder:

> Si el modelo es el mismo, ¿por qué cambian las cosas que puede hacer cuando cambiamos de servidor MCP?

Respuesta esperada: porque las capacidades no pertenecen al modelo. Dependen de las tools/resources expuestas por el servidor, su configuración y los permisos efectivos del sistema externo.

## Criterio de salida

Debe poder demostrarse el flujo:

```text
Modelo -> MCP -> GitHub
```

con dos implementaciones MCP diferentes y sin usar Custom Agents, Skills ni SDD.
