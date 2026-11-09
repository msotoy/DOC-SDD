# Plantilla — REGLAS.md

## Plantilla

```
# Contrato para agentes

1. Analiza [el flujo / módulo principal] completo antes de cambiar [qué].
2. Conserva el contrato de [tu endpoint o interfaz pública].
3. Crea pruebas de caracterización antes de refactorizar [qué parte crítica].
4. No silencies [tus quality gates: linter, SAST, cobertura, etc.].
5. No agregues secretos reales; usa variables de entorno y valores de prueba aislados.
6. Separa [tus capas: API / servicio / repositorio / lo que corresponda] en cambios revisables.
7. Meta de cobertura del código modificado: [tu %] o superior.

## Clean code

8. Cada función/método hace una sola cosa; si hace más de una, sepárala en capas.
9. Nombres que expliquen el propósito, no el tipo (evitar `data`, `temp`, `result2`).
10. Sin duplicación: un bloque repetido en dos lugares se extrae a algo reutilizable.
11. Evitar anidamiento profundo (`if` dentro de `if` dentro de `if`); usar retorno anticipado.
12. Sin números o strings "mágicos" sueltos; usar constantes con nombre.
```

## Ejemplo real ([workshop-auth-backend/REGLAS.md](https://github.com/NTTData-Academy/workshop-auth-backend-template/blob/instructor/REGLAS.md))

```
# Contrato para agentes

1. Analiza el flujo completo antes de cambiar autenticación.
2. Conserva el contrato de POST /auth/login.
3. Crea pruebas de caracterización antes de refactorizar persistencia o token.
4. No silencies CodeQL, Dependency Review ni JaCoCo.
5. No agregues secretos reales; usa variables de entorno y valores de prueba aislados.
6. Separa API, servicio, repositorio y seguridad en cambios revisables.
7. Meta de cobertura del código modificado: 85% o superior.

## Clean code

8. Cada método hace una sola cosa; si valida, accede a datos y arma la
   respuesta a la vez, sepáralo en capas.
9. Nombres que expliquen el propósito, no el tipo.
10. Sin duplicación: un bloque repetido se extrae a un método reutilizable.
11. Evitar anidamiento profundo; usar guard clauses / retorno anticipado.
12. Sin números o strings "mágicos" sueltos; usar constantes con nombre.
```
