# Contención de derivados dermatológicos

Base: PR131 `3cc5139b149feef390e6ceaa7358e2425d92620a`.
Rama aislada: `codex/dermatology-admission-20261127`.

La preparación de fase2 produjo cinco PNG de cuatro activos, incluidos los dos
frames del mismo archivo Commons. La guarda anterior reconocía 26 identidades
de archivo:24 originales y dos derivados anteriores. Los cinco nuevos hashes
no estaban en el índice. Fuera del directorio dermatológico reservado, una copia
de esos bytes no se reconocía como parte del corpus protegido.

El manifiesto incorpora ahora un bloque de contención, enlazado al SHA-256 del
recibo `FASE2/DERMA/ASSET_FINALITY_UPDATE_24.json`. Cada registro une el activo,
hash original, índice de frame y hash de su derivado. Un digest fijado en código
impide borrar, sustituir o reasignar esos registros mediante metadatos. La guarda
comprueba31 hashes exactos; conserva el digest original de los24 activos/23 casos.
No se incluyen imágenes, rutas de originales ni información de pacientes.

Esta ampliación **deniega** la inclusión de esos bytes. No concede permiso de
producto, redistribución, entrenamiento, evaluación independiente ni transferencia
a servicios externos. Las13 preparaciones locales, nueve contextos pendientes,
dos caras excluidas y23 decisiones médicas conservan su alcance. Los términos de
copyright ya verificados y la atribución no se sustituyen por nuevos requisitos
de permiso: la suficiencia de privacidad para una finalidad nueva sigue siendo
una cuestión distinta, y no se infiere ausencia de consentimiento.

## Verificación

-19 pruebas Node, incluidas cuatro nuevas: registro exacto, alteraciones de
  evidencia, invariancia de orden y copia sintética renombrada fuera del espacio
  reservado.
-11 pruebas Vitest, incluidas dos nuevas, con cobertura medida de la guarda.
-Prueba local de los cinco derivados reales: copias temporales renombradas y sin
  extensión fuera del espacio reservado fueron detectadas por hash. Las copias
  temporales se eliminaron, los derivados fuente permanecieron intactos y ningún
  píxel entró en Git ni se transmitió a agentes externos.
-Uso focal del servidor Emergency MCP existente:initialize/list_tools y
  get_pending_tasks de la instantánea explícita de coordinación, sin repetir votos.

La contención se limita a identidades exactas y al espacio reservado existente;
no es reconocimiento visual, detección universal de transformaciones ni garantía
de privacidad en carpetas ignoradas. Los avisos y umbrales de CI no cambian.

## Corrección de frontera del escáner sobre PR133

Base: `7df868d501b7271b2bbd2571e141b70656b251f8`. Se elimina la exclusión
por nombre de carpeta a cualquier profundidad: `dist`, `coverage` o
`node_modules` dentro de `app/public` podían ocultar bytes protegidos que Vite
publicaría. Las exclusiones son ahora rutas exactas relativas a la raíz:
`.git`, `node_modules`, `dist`, `coverage`, `__pycache__`, `.pytest_cache`,
`.venv`, `.cache`, `app/node_modules`, `app/dist`, `app/coverage` y
`tools/blood-gas-ocr/node_modules`, únicamente
cuando la entrada es un directorio real. Todos los enlaces y junctions se
rechazan antes de aplicar las exclusiones, incluso `app/node_modules`.
Un archivo raster llamado `dist` sin extensión tampoco queda excluido.

Verificación focal adicional: 23/23 pruebas Node y 14/14 Vitest, con archivos
sintéticos en varias profundidades de `public`, los tres espacios reservados,
nombres de archivo engañosos y enlaces bajo rutas públicas y de dependencias.
La configuración focal de Vitest reutiliza dependencias locales existentes;
no instala paquetes ni sustituye la CI completa. No cambia el manifiesto ni
la admisión de ningún activo.

La ruta exacta de dependencias OCR figura en la instalación de CI
(`npm ci --prefix tools/blood-gas-ocr`). Sus enlaces internos `.bin` pertenecen
a esa frontera de dependencias, como los de `app/node_modules`. Una copia del
nombre de ruta bajo `app/public` sigue inspeccionándose. Las pruebas adicionales
reproducen este árbol con un enlace sintético: 24/24 Node y 15/15 Vitest. Se
conserva la comprobación del repositorio real; no se excluyen directorios
temporales arbitrarios ni se relajan los controles de enlaces públicos.

```powershell
npm.cmd run security:dermatology:test --prefix app
node app/scripts/check-dermatology-asset-admission.mjs
```

No fusión, despliegue, modificación de cálculos, canon clínico ni last_checked.
CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.
