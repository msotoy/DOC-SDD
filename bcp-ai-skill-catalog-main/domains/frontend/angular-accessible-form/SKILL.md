---
name: angular-accessible-form
description: 'Usa esta skill cuando el agente deba crear o modificar un formulario en un proyecto Angular, para asegurar validación reactiva, mensajes de error accesibles y buenas prácticas de UX.'
---

## Propósito
Estandarizar la construcción de formularios en Angular: validación reactiva,
accesibilidad (labels, aria-*, foco en error) y manejo consistente de estados
de carga/error.

## Entradas
- Campos requeridos del formulario y sus reglas de validación.
- Contexto del proyecto: versión de Angular, si usa Reactive Forms o
  Template-driven Forms, librería de UI (si aplica).

## Salidas
- Formulario con `ReactiveFormsModule` y `FormGroup`/`FormControl`
  explícitos, salvo que el proyecto ya use Template-driven de forma
  consistente.
- Cada campo con `<label>` asociado, mensajes de error visibles y
  `aria-invalid`/`aria-describedby` cuando corresponde.
- Manejo de estado de envío (loading, error, éxito) sin bloquear el foco del
  usuario.

## Flujo
1. Confirmar el enfoque de formularios ya usado en el proyecto (reactive vs
   template-driven) antes de introducir uno nuevo.
2. Definir el `FormGroup` con validadores síncronos y, si aplica,
   asíncronos.
3. Enlazar cada control a su `<label>` y agregar mensajes de error
   accesibles.
4. Manejar el submit con feedback claro de loading/error/éxito.
5. Sugerir tests unitarios de las validaciones críticas.

## Constraints
- No dejar un input sin `<label>` asociado o `aria-label`.
- No usar solo color para indicar error (agregar texto o ícono con
  descripción).

## Adaptación
- Si el proyecto usa una librería de componentes (Angular Material, PrimeNG,
  etc.), preferir sus componentes de formulario sobre HTML plano.
