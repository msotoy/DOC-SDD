# Suscribir un repo nuevo al skills-catalog

## 1. Registrar el repo en el catálogo
Agregar una entrada en `subscribers.json` de este repo, indicando el nombre
completo del repo (`org/repo`) y los dominios que le interesan:

```json
{ "repo": "NTTData-Academy/nuevo-repo", "domains": ["backend"] }
```

Esto es informativo (para saber qué repos consumen qué) — el dispatch a
todos los suscriptores se hace igual desde `notify-subscribers.yml`.

## 2. Copiar el workflow al repo consumidor
Copiar `docs/consumer-workflow-template.yml` a
`.github/workflows/sync-skills.yml` en el repo nuevo, y editar la lista de
`sparse-checkout` con los mismos dominios declarados en el paso 1.

## 3. Configurar el token (si el catálogo es privado)
- Crear un PAT (o usar un GitHub App) con permiso de lectura sobre
  `skills-catalog`.
- Guardarlo como secret `CATALOG_READ_TOKEN` en el repo consumidor.
- En `skills-catalog`, agregar/confirmar que el token usado en
  `CATALOG_DISPATCH_TOKEN` (secret del propio catálogo) tenga permiso para
  disparar `repository_dispatch` sobre el repo consumidor.

## 4. Primera sincronización
Ejecutar el workflow manualmente la primera vez
(`workflow_dispatch` desde la pestaña Actions) para poblar
`.github/skills/` sin esperar al próximo cambio en el catálogo.

## 5. Revisar el PR automático
El workflow abre un PR (`chore/sync-skills-catalog`) con las skills
sincronizadas. Revisarlo y mergearlo como cualquier otro cambio — así queda
un historial claro de qué skill cambió y cuándo en cada repo.
