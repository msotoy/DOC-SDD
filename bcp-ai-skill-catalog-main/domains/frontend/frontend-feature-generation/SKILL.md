---
name: frontend-feature-generation
description: Genera funcionalidades frontend con componente, servicio, rutas, estados, accesibilidad y pruebas.
---

# Frontend Feature Generation Skill

## Proposito
Convertir un contrato API o historia de usuario en una funcionalidad frontend coherente con el framework y las convenciones del squad.

## Entradas
- Historia de usuario y criterios de aceptacion.
- Contrato API.
- Framework y version: Angular, React, Vue u otro aprobado.
- Patrones de rutas, estado, estilos y accesibilidad.
- Comandos de build y test existentes.

## Salidas
- Componente o pantalla.
- Servicio de datos o cliente API.
- Tipos y modelos.
- Ruta, guard o estado cuando aplique.
- Estados loading, empty, error y success.
- Tests unitarios o de componente.
- Documentacion de configuracion.

## Flujo
1. Inspecciona la arquitectura frontend existente.
2. Mapea criterios de aceptacion a estados y acciones.
3. Implementa usando los patrones del repositorio.
4. Usa configuracion externa para URLs.
5. Verifica accesibilidad, mensajes seguros y responsive behavior.
6. Ejecuta lint, build y tests.

## Reglas
- No duplicar logica de HTTP o sesion.
- No usar `innerHTML` para contenido dinamico.
- No guardar tokens en `localStorage` salvo excepcion aprobada.
- No introducir dependencias sin autorizacion.
- No ocultar errores del backend.

## Adaptacion
El Frontend Chapter Lead define framework, estructura, state management, UI kit, cobertura y reglas de accesibilidad.
