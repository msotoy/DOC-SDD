# Arquitectura Hexagonal y Validación Determinista

> **Módulo de Referencia Técnica · BCP AI Lab (Día 04)**  
> *Alineado con Sesión 2 (`s2_langgraph`) y las evaluaciones de Sesión 4 (`s4_guardrails`).*

---

## 1. ¿Por qué Arquitectura Hexagonal en Sistemas con IA?

Cuando un modelo de lenguaje (LLM) genera código a partir de un requerimiento en lenguaje natural, existe un riesgo intrínseco de generar **código acoplado**: controladores REST que ejecutan queries SQL directas, entidades JPA usadas como modelos de vista en el frontend o lógica de negocio mezclada con llamadas HTTP.

El arquetipo de **Arquitectura Hexagonal (Puertos y Adaptadores)** se aplica en el BCP para que el código generado por IA sea **validable de forma determinista y matemática**:
* El **dominio** no depende de frameworks, bases de datos ni bibliotecas externas.
* Las dependencias fluyen estrictamente hacia adentro: `infrastructure → application → domain`.
* Si el LLM intenta importar un paquete de infraestructura dentro del dominio, el validador automático lo detecta y rechaza el código antes de desplegar.

---

## 2. Las 7 Capas del Arquetipo Bancario BCP

El arquetipo hexagonal se estructura en exactamente 7 capas dentro de `output/hex/`:

```text
output/hex/
├── domain/
│   ├── model/                  ← Entidades puras y objetos de valor (User, LoginAttempt…)
│   └── port/
│       ├── input/              ← Interfaces de entrada / Casos de uso (LoginUseCase, AuthPort…)
│       └── output/             ← Interfaces de salida / Repositorios SPI (UserRepository, TokenService…)
├── application/
│   └── service/                ← Orquestación de casos de uso (implementa input ports, consume output ports)
└── infrastructure/
    ├── adapter/
    │   ├── input/              ← Adaptadores primarios: Controladores REST, CLI, recursos HTTP
    │   └── output/             ← Adaptadores secundarios: Implementaciones JPA, clientes HTTP, BCrypt
    └── config/                 ← Configuración de inyección de dependencias, beans y properties
```

### Reglas de Dependencias Obligatorias

| Capa | Puede importar de... | NUNCA puede importar de... |
| :--- | :--- | :--- |
| **`domain/model`** | Solo tipos estándar de Java | `application`, `infrastructure`, frameworks |
| **`domain/port/*`** | `domain/model` | `infrastructure`, `application` |
| **`application/service`**| `domain/model`, `domain/port/*` | `infrastructure` (JPA, RESTEasy, Spring Web) |
| **`infrastructure/*`** | `application`, `domain`, librerías externas | — (es la capa más externa) |

---

## 3. `hex_archetype.py`: Scaffold y Validación Automática

Presente en `s1_crewai` y `s2_langgraph` — las sesiones que **generan** código desde cero.

> **S3 y S4 no lo usan.** Refactorizan repositorios ajenos, que no tienen por qué seguir arquitectura hexagonal; exigirla daría un veredicto RECHAZADO en cada corrida sin que eso signifique nada. La validación hexagonal sólo tiene sentido cuando controlas la estructura desde el primer archivo.

Expone:

```python
HEX_LAYERS        # Lista de las 7 capas obligatorias
HEX_PROMPT_PREFIX # Prompt inyectado al LLM para forzar paquetes y arquitectura

scaffold(output_dir, feature_title)  # Crea carpetas + ARCHITECTURE.md si faltan
validate_structural(output_dir)      # OUT-HEX-01: Cada capa tiene al menos un archivo
validate_semantic(output_dir)        # OUT-HEX-02: Escanea imports prohibidos con Regex
validate(output_dir)                 # Ejecuta ambas y retorna dict {passed, summary}
```

### Validación Estructural (`OUT-HEX-01`)
Comprueba que cada una de las 7 capas contenga archivos reales de código (no solo archivos `.gitkeep` vacíos).

### Validación Semántica (`OUT-HEX-02`)
Escanea los archivos `.java`, `.ts` y `.py` dentro de `domain/` y `application/` mediante tres expresiones regulares, para cubrir la sintaxis de import de cada lenguaje:

```python
_INFRA_PATTERNS = [
    re.compile(r"from\s+infrastructure[.\s]"),        # Python / TypeScript
    re.compile(r"import\s+infrastructure[.\s]"),      # import directo
    re.compile(r"import\s+[\w.]*\.infrastructure\b"),  # Java (paquete calificado)
]
```

Una sola violación indica que la lógica de negocio conoce detalles técnicos de persistencia o transporte, lo que hace que el veredicto sea **RECHAZADO**.

---

## 4. Verificación sin Gastar Tokens (`test_hex_wiring.py`)

Para verificar que el arquetipo y las validaciones funcionan correctamente en tu entorno sin llamar al LLM ni consumir cuota:

```powershell
cd s2_langgraph
python test_hex_wiring.py
```

Este script comprueba:
1. Que el mapeo de archivos (`FILE_MAP`) apunte a capas válidas de `HEX_LAYERS`.
2. Que `scaffold()` cree la estructura de 7 capas correctamente.
3. Que `validate()` apruebe un backend limpio y rechace uno con imports indebidos.
