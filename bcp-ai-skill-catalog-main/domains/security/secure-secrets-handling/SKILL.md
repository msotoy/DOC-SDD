---
name: secure-secrets-handling
description: 'Usa esta skill cuando el agente vaya a generar o revisar código, configuración o pipelines CI/CD que involucren credenciales, tokens, API keys o connection strings, para evitar que queden hardcodeados o expuestos.'
---

## Propósito
Evitar que credenciales, tokens y secretos queden hardcodeados en código,
archivos de configuración o logs, y guiar el uso correcto del gestor de
secretos corporativo.

## Entradas
- Fragmentos de código o configuración que el agente está generando o revisando.
- Contexto del pipeline CI/CD, si aplica.

## Salidas
- Código o configuración sin secretos embebidos.
- Referencias a variables de entorno o al gestor de secretos corporativo
  (Vault, AWS Secrets Manager, Azure Key Vault, según lo declarado en el repo).
- Alerta explícita si se detecta un secreto ya existente en el código.

## Flujo
1. Detectar patrones de credenciales (API keys, tokens, contraseñas,
   connection strings) en el contenido generado o revisado.
2. Si aparece un secreto embebido, reemplazarlo por una referencia a variable
   de entorno o al gestor de secretos.
3. Documentar en un comentario breve cómo debe configurarse ese secreto fuera
   del código.
4. Señalar explícitamente al usuario cualquier secreto preexistente encontrado
   en el repo.

## Constraints
- Nunca imprimir el valor real de un secreto, ni siquiera parcialmente.
- No sugerir almacenar secretos en archivos versionados (`.env` commiteado,
  `application.yml` con valores reales, etc.).
- Alinear siempre con la política interna de gestión de secretos vigente.

## Adaptación
- Ajustar el nombre del gestor de secretos según el stack declarado en el
  repo consumidor (Vault, AWS Secrets Manager, Azure Key Vault, etc.).
