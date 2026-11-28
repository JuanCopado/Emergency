# IMP — inventario técnico reutilizable

Observación Codex: 27/11/2026. Base inspeccionada `1703435de7002172d14ed32b94df1dc6b07f4314`, rama `docs/implementacion-viva-20261127` (PR134). Alcance: inspección estática y metadatos actuales de GitHub; **no ejecución de pruebas de producto ni auditoría externa**. Este inventario no cierra IMP-03 ni sus dependencias. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.

## Componentes existentes y límites

| Capacidad | Evidencia en la base | Reutilización y límite |
|---|---|---|
| Aplicación React/TypeScript/Vite | `app/package.json:8`, `app/vite.config.ts:27` | Compilar la aplicación existente; no reconstruir frontend ni motores. `npm run build` comprueba corticoides, genera guías/procedimientos/pediatría, ejecuta TypeScript y Vite. |
| Dependencias de frontend reproducibles | `app/package-lock.json`; `.github/workflows/app-ui-qa.yml:83` | Reutilizar `npm ci --ignore-scripts` seguido del postinstall explícito revisado; conservar guardas picomatch. No instalar paquetes nuevos para empaquetar archivos. |
| Identidad del build | `app/scripts/build-identity.mjs:13`, `app/vite.config.ts:17`, `app/src/test/build-identity.test.tsx` | SHA y estado dirty desde Git con rutas fijas y configuración global ignorada; un archivo sin `.git` obtiene identidad desconocida. Construir en checkout limpio y congelar el artefacto después. |
| PWA y caché offline | `app/vite.config.ts:99–127`, `app/src/main.tsx:11` | Workbox precache de recursos estáticos; `registerType: autoUpdate`; denylist `/api/` evita HTML como respuesta API. No hay aquí caché de respuestas clínicas autenticadas. |
| Verificación offline existente | `app/scripts/check-pwa-offline.mjs:1–7`, `:66–76`, `:92–117` | El arnés instala el worker real, apaga servidor y conexión, prueba siete rutas y el resultado local de perfusión, y rechaza fallback HTML en API. No acredita que todas las funciones clínicas funcionen sin backend. |
| Nota en memoria | `app/src/clinical-note/draft.tsx:52–63`, `app/src/test/clinical-note-navigation.test.tsx:31–32` | Un episodio en React, sin persistencia de paciente en local/sessionStorage; se pierde al cerrar/recargar. Mantener advertencia de salida y no forzar actualización que destruya el borrador. |
| Preferencias locales | `app/src/state/settings.tsx:19–20`, `:34–40`, `:64–69`; `app/src/lib/storage.ts:1–12` | Idioma, tema y unidad visual en localStorage. Estas preferencias pueden tener una futura réplica remota separada del caso clínico. |
| Cliente clínico | `app/src/clinical-note/api.ts:3`, `:31–39` | `VITE_CLINICAL_NOTE_API_BASE` es configurable; las peticiones POST llevan `cache: no-store`. Un empaquetado local debe verificar que la base no se cambió a un destino remoto. El default vacío por sí solo no demuestra ausencia de egreso en cualquier build. |
| Perímetro local JS | `app/scripts/clinical-api-boundary.mjs:1–6`, `:25–44`, `:47–63` | Token efímero permanece en proceso Node, Host/Origin/peer loopback; la API sin sesión configurada responde 503 JSON. El proxy solo admite origen IPv4 loopback directo. No es autenticación de usuario. |
| Perímetro local Python | `clinical/scripts/clinical_http_boundary.py:1–4`, `:17–34`, `:37–57` | Credencial del proceso proxy, no del médico; bind/orígenes locales y credencial de 256 bits. No retirar estas restricciones para crear un servicio público. |
| Contratos/motores Python | `clinical/scripts/clinical_note_api.py:541–638`, `:735–770` | `dispatch(path, payload)` reutiliza motores/catálogos/exportadores ya existentes. `make_server` y CLI prohíben exposición no loopback. Adaptador productivo posterior separado, con autorización por ruta, sin saltarse validaciones ni ejecutar indiscriminadamente todos los endpoints. |
| Transporte acotado | `clinical/scripts/http_transport.py:19–43`, `:78–128` | Rechaza framing ambiguo/cuerpos simples; timeout y semáforo limitan recursos. Basado en `http.server`, no un servidor ASGI de producción. |
| Exportación | `clinical/scripts/clinical_note_api.py:519`, `:624–637`; `clinical/requirements.txt` | Exportadores existentes con ReportLab 5.0.1 y Pillow 13.0.0; no duplicar motor PDF/DOCX ni sustituir su validación terapéutica. |
| Controles de producto | `app/scripts/build-dependency-guard.mjs`, `app/scripts/check-lab-exclusion.mjs`, `.github/workflows/app-ui-qa.yml:95–116` | Conservar auditoría del bundle/worker y exclusión de laboratorio. No publicar checkout, fixtures, fuentes restringidas, mapas de desarrollo o evidencias del laboratorio como parte de la instalación. |

Los números de línea corresponden a la base inspeccionada. El recibo externo conserva SHA-256 de los archivos leídos; no se atribuyen estas observaciones a código introducido después.

## Candidatos de laboratorio actuales

GitHub se consultó directamente el 27/11/2026. Todas las PR siguientes continúan abiertas, en borrador y sin fusionar. Los PASS/MERGE_READY que sus descripciones consignan son evidencia histórica declarada por cada entrega, **no pruebas repetidas por este inventario**.

| PR | HEAD exacto | Alcance reutilizable y límite |
|---|---|---|
| [129](https://github.com/JuanCopado/Emergency/pull/129) | `a3ae85412a868c105c64ca8b491e1cb3a1df065c` | RAG extractivo autorizado y guardas de admisión de activos; sin red/LLM, extractos LOCAL_ONLY. |
| [130](https://github.com/JuanCopado/Emergency/pull/130) | `f32d211eed6a7baa7c42aadae583f6726e9e7e9b` | Intercambio FHIR/HL7 y permisos temporales sintéticos; sin identidad institucional ni conexión hospitalaria. |
| [131](https://github.com/JuanCopado/Emergency/pull/131) | `3cc5139b149feef390e6ceaa7358e2425d92620a` | Ranking híbrido y pasarela local sintética; no OIDC ni transporte LLM real. |
| [132](https://github.com/JuanCopado/Emergency/pull/132) | `780cf736b29d9e176a850530797115c32638aab0` | MCP local stdio, ocho herramientas de solo lectura y fuentes fijadas; no API multiusuario de red. |
| [133](https://github.com/JuanCopado/Emergency/pull/133) | `e4d3f71975a75389bbc9df146670b5823ce4677b` | Laboratorio RAG/exchange/buscador; el navegador nuevo conserva límites de política documentados. No constituye infraestructura de implantación. |

No incorporar estos candidatos automáticamente a PR134 ni trasladar sus auditorías a un SHA diferente.

## Herramientas e infraestructura observadas

- Node `v24.15.0` y Python `3.13.17` ejecutados con `--version` en este proceso Windows. La CI existente especifica Node 22/Python 3.12; no confundir disponibilidad local con matriz de soporte validada.
- `Get-Command docker,psql` no resolvió ejecutables en PATH. Esto no demuestra que no existan instalaciones fuera de PATH; no se instalaron ni configuraron servicios.
- Búsqueda de fuentes ejecutables en `app/src`, `clinical/scripts`, `tools` y `security`: no implementación FastAPI/Starlette/ASGI, OIDC/JWKS, SQLAlchemy/psycopg o servidor PostgreSQL en la base inspeccionada. La propuesta documental los menciona como opciones, no capacidades instaladas.
- No se localizaron Dockerfile, Compose, Terraform o migraciones `.sql` versionadas bajo `.github`, `tools`, `app` y `clinical/scripts` en esta base. No afirmar contenedores o restauración de PostgreSQL operativos.
- `clinical/requirements.txt` fija dos runtimes; la CI usa `security/requirements-ci.txt` con `--require-hashes`. No crear un lock paralelo sin necesidad; separar dependencias de desarrollo/auditoría del mínimo distribuido.

## Incremento mínimo recomendado para IMP-03

Implementar después de cotejar IMP-00, en área nueva `tools/local-installation/`, con biblioteca estándar y pruebas aisladas. No modifica aritmética clínica ni exige proveedor/IdP remoto para modo referencia.

1. **Construcción:** aceptar únicamente build de checkout y SHA conocidos, configuración explícita sin destino API remoto y sin flags de laboratorio; ejecutar guardas y build existentes. Paquete limitado a `app/dist` y lanzador revisado. No copiar repositorio, secretos, `node_modules`, fuentes de préstamo ni datos de usuario.
2. **Manifiesto:** versión de esquema, SHA fuente, configuración relevante, capacidades incluidas/excluidas, ruta/tamaño/SHA-256 de cada archivo y longitud total acotada. Verificar por un digest o firma confiable independiente del propio archivo; manifiesto+ZIP autodeclarados detectan corrupción, no autentican al editor. No denominar “firmado” a un paquete que solo tenga hashes.
3. **Recepción:** rechazar traversal, rutas absolutas/UNC/unidades Windows/ADS, enlaces/reparse points, duplicados por casefold, archivos extra/ausentes y límites de compresión/tamaño. Extraer en staging propiedad de la instalación, comprobar todo antes de activar.
4. **Instalación/actualización:** directorios inmutables por versión y puntero de activación reemplazado atómicamente; no sobreescribir versión activa ni borrar versiones anteriores durante la recepción. Fallo deja versión previa seleccionada.
5. **Lanzador:** servir archivos compilados con listener fijo `127.0.0.1`, Host y peer exactos, cabeceras de seguridad, sin listados, enlaces ni acceso al checkout. No Vite dev/preview público. API no habilitada devuelve error JSON explícito sin shell; llamadas remotas del caso deshabilitadas por defecto.
6. **Rollback:** seleccionar versión verificada anterior. Probar también el estado del navegador: el worker `autoUpdate` puede mantener una versión distinta de la carpeta seleccionada. Verificar identidad tras recarga/control del worker y documentar transición segura del episodio. No prometer rollback efectivo solo por cambiar un puntero.
7. **Verificación:** paquete reproducible, rechazo de manipulación/traversal/enlaces, actualización fallida conserva activo, rollback y archivos extra rechazados; smoke sintético en navegador con buildidentity. Reutilizar arnés offline existente para las rutas que realmente soporta; comprobar `/api` nunca da HTML. No exigir repetir toda la QA clínica por un empaquetador independiente si no cambia el producto.

Matriz explícita del paquete estático: inicio, referencias, guías, procedimientos, preferencias y cálculo local de perfusiones tienen arnés offline existente; nota con análisis/exportación, scores y cálculos que llaman al API **no se vuelven locales por empaquetar el frontend**. Un paquete estático es una instalación parcial transparente, no implantación funcional completa. El backend local reproducible puede añadirse como incremento posterior mediante los contratos existentes, sin exposición de red ni PHI remota.

## Puente posterior hacia IMP-04–07

El adaptador productivo debe separar referencia pública, identidad/cuenta/preferencias y entrada del caso; por defecto no admitir PHI remota. Reutilizar funciones de los motores detrás de rutas permitidas y contratos versionados, con límites de tamaño/tasa/tiempo, origen único, denegación de egress y errores sin eco. El endpoint local y su token no sustituyen OIDC ni autorización por usuario. No trasladar objetos libres o archivos al gateway hasta disponer de alcance, validación y tratamiento autorizado.

Elegir stack ASGI/IdP/PostgreSQL solo después de IMP-00/01/02. IMP-05 requiere proveedor sintético y pruebas issuer/audience/nonce/state/PKCE, rotación, revocación y acceso cruzado; IMP-06 requiere migraciones y restore PostgreSQL reales con cuentas sintéticas, sin tabla de episodios. Una maqueta o SQLite no acredita PostgreSQL. IMP-07 requiere contenedor no-root, configuración cerrada, respaldo cifrado y restauración medida; la ausencia de Docker/psql en PATH es un límite de ejecución de pruebas local, no permiso de instalar servicios o provisionar nube.

## Pruebas existentes que conviene reutilizar

- `app/scripts/build-identity.test.ts`, `app/src/test/build-identity.test.tsx`: identidad/dirty y archivos sin repositorio.
- `app/scripts/clinical-api-boundary.test.ts`, `clinical-api-boundary-direct.test.ts`: fronteras y destino de proxy.
- `clinical/tests/test_clinical_http_boundary.py`: credenciales duplicadas/ausentes, origen/Host, todas las familias POST, salud mínima y rechazo de exposición no loopback.
- `clinical/tests/test_http_transport_security.py`: framing, deadlines absolutos, recursos y TLS con fixture sintético.
- `app/src/test/clinical-note-navigation.test.tsx`: estado de episodio y ausencia en almacenamiento del navegador.
- `app/scripts/check-pwa-offline.mjs`, `build-dependency-guard.node-test.mjs`, `check-lab-exclusion.mjs`: offline real y separación del bundle.

Estas pruebas fueron localizadas y leídas por este inventario; no se reportan como ejecutadas de nuevo. El responsable de cada incremento registra comando, SHA y resultado real al ejecutarlas.

## Especificación de pruebas IMP-03 preparada, no ejecutada

Esta matriz define pruebas del instalador/servidor nuevos; no sustituye IMP-00 ni afirma implementación. Biblioteca estándar `unittest`, `tempfile`, `zipfile`, `hashlib`, `http.client`, `socket` y `threading`. Cada fixture debe construirse en directorio temporal propio, con datos inertes, listener loopback y puertos efímeros; terminar todos sus hilos y sockets al finalizar. No leer ni activar versiones de una instalación ajena.

| Grupo / prueba propuesta | Estímulo | Resultado exigido |
|---|---|---|
| `test_trusted_manifest_digest_required` | Digest externo ausente, inválido o distinto; paquete y manifiesto alterados juntos | Rechazo antes de extracción/activación. El digest esperado viene de un canal confiable separado, no de un archivo junto al ZIP. |
| `test_archive_paths_are_closed` | `../`, rutas absolutas/UNC, unidad `C:`, ADS `x:y`, separadores Windows, dotsegments, controles/NUL, rutas vacías | Rechazo íntegro antes de escribir fuera del staging. Canonicalización explícita independiente del SO anfitrión. |
| `test_archive_entries_are_unique` | Ruta repetida, colisiones casefold, un archivo que también es padre de otro, alias por separador | Rechazo; nunca “último archivo gana”. |
| `test_links_and_reparse_points_rejected` | Entrada ZIP symlink/mode especial; destino/staging/root con enlace o reparse point | Rechazo sin atravesar el enlace ni alterar la diana. En Windows se documentan negativos de reparse realmente ejecutados, no se simulan como equivalentes. |
| `test_archive_limits_before_extract` | Demasiadas entradas, total declarado excesivo, compresión desproporcionada, archivo individual grande | Rechazo acotado antes de expansión; contar también bytes realmente leídos para no confiar solo en cabeceras ZIP. |
| `test_exact_manifest_file_set` | Archivo extra, ausente, duplicado, tamaño o SHA falsos; manifiesto de tipo/esquema incorrecto | Rechazo completo, sin activación parcial. No permitir directorios o campos desconocidos que alteren semántica. |
| `test_install_version_immutable` | Instalar versión ya existente con bytes distintos o nombre inseguro | Rechazo; no sobrescribir versión activa ni reutilizarla como staging. |
| `test_failed_update_keeps_previous` | Corrupción en último archivo, error de extracción o fallo antes del reemplazo del puntero | Puntero y versión anterior permanecen utilizables; cleanup solo del staging propio. |
| `test_atomic_selection_and_single_writer` | Dos recepciones concurrentes; interrupción entre staging y activación | Un único escritor o compare-and-swap que no pierda la versión previa. Puntero completo o anterior, nunca JSON truncado. |
| `test_activation_and_rollback_reverify` | Activar versión válida, manipularla después, intentar activación/rollback | Revalidación íntegra al seleccionar/servir; selección alterada rechazada. El rollback selecciona versión previa válida y no borra ninguna. |
| `test_host_peer_and_origin_closed` | Host ausente/duplicado/externo, peer externo, Origin extranjero/duplicado/null | Denegar antes de servir; el permiso de GET sin Origin para navegación inicial no acepta orígenes ajenos. No CORS permisivo. |
| `test_api_never_gets_shell` | GET/POST/HEAD/OPTIONS a `/api` y `/api/*`, con query y rutas codificadas | Respuesta de API 503 JSON fija cuando deshabilitada; nunca `index.html`; HEAD sin cuerpo; métodos no admitidos rechazados y sin eco. |
| `test_static_paths_and_fallback` | Ruta SPA legítima, fichero permitido, fichero oculto/ausente, directory listing, traversal codificado/doblecodificado | Shell solo para navegación SPA prevista; nunca contenido fuera del artefacto/manifiesto, listado, `.git`, secretos o fichero extra. |
| `test_security_headers_and_logging` | Documento inicial, recursos, errores con URL/query sintética sensible | CSP conectividad propia y sin origen externo/unsafe-eval; nosniff, referrer, frame/base/form cerrados; logs no contienen path/query/cuerpo/token. No copiar CSP dev con refresh/websocket. |
| `test_build_local_configuration` | Base API remota, flags LAB, build desconocido/dirty o inputs alterados | Paquete local rechazado; ninguna inyección de credenciales en `VITE_*`; manifiesto conserva identidad exacta y capacidades reales. |
| `test_roundtrip_real_static_http` | Paquete mínimo válido → instalar → servir → actualizar → rollback | HTTP real desde `http.client` identifica bytes de cada versión y errores cerrados; no bastan llamadas directas a helpers. |
| `test_real_pwa_selection` (navegador) | Worker controla versión A; seleccionar B; volver A; borrador de episodio abierto | Comprobar buildidentity y control/caché reales en cada estado, sin autorecargar ni destruir el episodio. Si el worker conserva B al volver A, estado `BLOCKED_SAFE` y no PASS de rollback completo. |

**Criterio finito:** instalación/actualización/rollback de archivos y HTTP local pueden quedar verificados por separado. La identidad efectiva del cliente PWA requiere navegador real; si no se puede ejecutar, se entrega como pendiente específico con el servidor cerrado o modo que garantice no servir una versión inconsistente, sin declarar IMP-03 completo. La protección mediante hash externo no se llama firma criptográfica. La referencia estática parcial no se llama backend local funcional.

**Artefacto anterior localizado:** existe `Emergency/app/dist` en el checkout histórico `ab48eaf`, donde el propietario mantiene catálogos generados modificados. No se reutiliza como build limpio de `1703435`/`81b231c`. Se pueden reutilizar dependencias instaladas solo tras comprobar lock/plataforma e independencia de la nueva copia; no trasladar su identidad, resultados o auditoría al build nuevo.
