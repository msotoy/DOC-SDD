# Levantar el laboratorio con Podman (o Docker)

Esta es una forma alternativa de levantar los 3 servicios **sin instalar Java,
Node ni Python en tu máquina** — todo corre dentro de contenedores. Si ya
tienes esas herramientas instaladas, la vía normal (ver `README.md`) es más
simple. Usa esto si no las tienes, o si prefieres no instalarlas.

No hace falta tocar los 3 repos (`workshop-*-template`): el `compose.yaml`
usa imágenes genéricas (Maven, Python, Node) y monta tu código como carpeta
compartida, igual que si lo corrieras a mano.

## ¿Podman o Docker?

Da igual — son dos programas distintos que hacen lo mismo y entienden el
mismo archivo (`compose.yaml`). Si tienes Podman, usa `podman compose`; si
tienes Docker, usa `docker compose`. El resto de los comandos son idénticos.
Esta guía usa `podman`; donde diga `podman` puedes poner `docker`.

## Paso 1 — Instalar Podman

Las máquinas del taller ya traen Podman instalado. En ese caso no hace falta
instalarlo de nuevo: verifica la versión y continúa directamente con el
**Paso 3** para instalar o comprobar `podman-compose`.

Descarga e instala [Podman Desktop](https://podman.io/) o el CLI de Podman.
Verifica que quedó instalado:

```powershell
podman --version
```

## Paso 2 — Inicializar la máquina (solo Windows/Mac, una vez)

Podman necesita una VM de Linux liviana para correr contenedores en Windows.
Se crea una sola vez:

```powershell
podman machine init
podman machine start
```

Si más adelante `podman ps` te dice que no puede conectar, probablemente la
máquina está apagada — repite `podman machine start`.

## Paso 3 — Instalar el complemento de compose

`podman` no trae el soporte de `compose.yaml` incluido en todas las
versiones; se instala aparte, una sola vez (necesita Python):

```powershell
py -m pip install --user podman-compose
```

En Windows, `pip` puede instalar `podman-compose.exe` en la carpeta de
scripts de Python sin agregarla al `PATH`. Comprueba que Podman lo detecta:

```powershell
podman compose version
```

Si aparece `looking up compose provider failed` o no encuentra
`podman-compose`, agrega la carpeta de scripts de Python al `PATH` de usuario
y abre una terminal nueva:

```powershell
$scriptsPath = Join-Path $env:APPDATA "Python\Python314\Scripts"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";" + $scriptsPath, "User")
```

> Ajusta `Python314` por la versión de Python que muestre `py --version`.

## Paso 4 — Clonar los 3 repos

Los tres repos viven en `reqflow-workspace/`, **al lado** de
`bcp-ai-lab-day-01` (no dentro), porque `compose.yaml` los monta usando rutas
`../reqflow-workspace/workshop-...`. Créalos como repos propios siguiendo el paso 1 de
[README.md](README.md#cómo-empezar) (clonar la plantilla, desvincularla y
publicarla bajo tu owner).

Comprueba el layout antes de continuar, parado en la carpeta del curso:

```powershell
Get-ChildItem -Name                       # bcp-ai-lab-day-01 y reqflow-workspace
Get-ChildItem -Name reqflow-workspace     # los 3 workshop-*
```

Después entra al laboratorio:

```powershell
cd bcp-ai-lab-day-01
```

> Si `reqflow-workspace/` no está al lado del laboratorio,
> `../reqflow-workspace/workshop-*` apunta a carpetas que no existen y los
> contenedores arrancan con `/app` vacío (ver *Problemas conocidos*).

## Paso 5 — Levantar los 3 servicios

Desde `bcp-ai-lab-day-01` (al lado de `reqflow-workspace/`):

```powershell
podman compose up -d
```

La primera vez descarga las imágenes base (puede tardar varios minutos).
Verifica que los 3 estén corriendo:

```powershell
podman compose ps
```

Y que respondan:

```powershell
curl http://localhost:8080/q/health
curl http://localhost:8000/docs
curl http://localhost:4200
```

Abre `http://localhost:4200` y entra con `student` / `Workshop123!`.

## Ver logs de un servicio

```powershell
podman compose logs -f frontend
podman compose logs -f auth-backend
podman compose logs -f requirements-api
```

## Apagar todo

```powershell
podman compose down
```

Esto no borra tu código (está montado desde tu carpeta real), solo apaga
los contenedores.

## Problemas conocidos

### Los 3 servicios fallan a la vez: `requirements.txt`, `package.json` o `pom.xml` no encontrados

Síntomas juntos: `Could not open requirements file`, `npm error enoent ...
/app/package.json` y `No plugin found for prefix 'quarkus'`. Significa que
`/app` está vacío: `reqflow-workspace/` no está al lado de la copia del
laboratorio desde la que levantaste el compose, y
`../reqflow-workspace/workshop-*` no apunta a tus repos. Baja todo
(`podman-compose down`), revisa el layout del Paso 4 y vuelve a levantar.

### `Unit user-libpod_pod_....slice was already loaded or has a fragment file`

`podman-compose` crea un *pod* por proyecto: los servicios comparten red y un
cgroup de pod que Podman le pide a systemd. En Podman sobre WSL (cgroups v1)
ese cgroup falla, y el slice de un intento fallido queda registrado. Por eso
`compose.yaml` ya trae `x-podman: in_pod: false`: cada servicio corre como
contenedor suelto en la red del proyecto y se hablan por nombre
(`auth-backend:8080`), igual que con Docker. Si usas una versión de
`podman-compose` que ignora esa clave, limpia y pasa el flag a mano:

```powershell
podman-compose down
podman pod ls                      # si sigue apareciendo el pod del lab:
podman pod rm -f <nombre-del-pod>
podman-compose --in-pod=false up
```

### `crun: controller 'pids' is not available under /sys/fs/cgroup/non-systemd/...`

WSL está corriendo en cgroups v1 y no expone el controlador `pids`, que
Podman usa para limitar procesos. Pasa igual en modo rootful y rootless.
Desactiva ese límite en la máquina de Podman y **recrea** los contenedores
(el límite se fija al crearlos, un `up` sobre contenedores viejos sigue
fallando):

```powershell
podman machine ssh "sudo mkdir -p /etc/containers/containers.conf.d && printf '[containers]\npids_limit = 0\n' | sudo tee /etc/containers/containers.conf.d/pids.conf"
podman-compose --in-pod=false down
podman-compose --in-pod=false up
```

Alternativa de fondo: pasar WSL a cgroups v2 con
`kernelCommandLine = cgroup_no_v1=all` en la sección `[wsl2]` de
`%USERPROFILE%\.wslconfig`, y luego `wsl --shutdown` y `podman machine start`.

### Error de certificado al descargar las imágenes (`x509: certificate signed by unknown authority`)

La primera vez que se crea la máquina de Podman en Windows, su base de
certificados puede venir incompleta y falla al descargar imágenes de
Docker Hub. Si te pasa:

```powershell
podman machine ssh -- sudo update-ca-trust
```

Si sigue fallando, descarga las 3 imágenes una vez de forma manual con
verificación desactivada (quedan cacheadas localmente, así que solo hace
falta una vez):

```powershell
podman pull --tls-verify=false docker.io/library/maven:3.9-eclipse-temurin-21
podman pull --tls-verify=false docker.io/library/python:3.13-slim
podman pull --tls-verify=false docker.io/library/node:24-slim
```

Después, `podman compose up -d` va a usar las imágenes ya descargadas sin
volver a tocar la red.

### El frontend fallaba con webpack/npm bug (`Cannot read properties of null (reading 'edgesOut')`)

Es un bug conocido de la versión de npm que trae la imagen `node:22`. Por
eso este `compose.yaml` usa `node:24` en vez de `node:22` — trae una
versión de npm más nueva que no tiene el bug. Si lo ves con otra imagen,
actualizar npm dentro del contenedor también lo resuelve.

### El frontend fallaba con `EACCES: permission denied` al instalar dependencias

Pasa cuando el repo está dentro de una carpeta sincronizada con OneDrive
(o similar): `npm install` hace renombres internos que a veces chocan con
el sincronizador. La solución ya está en el `compose.yaml`: `node_modules`
vive en un volumen propio de Podman, no en tu carpeta de Windows, así
nunca lo toca OneDrive. No deberías ver este error, pero si aparece con
otra configuración, esa es la causa.
