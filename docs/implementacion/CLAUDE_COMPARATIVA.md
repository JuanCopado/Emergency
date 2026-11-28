# Claude: contraste independiente IMP-00/01

Consulta real entregada sobre `1703435de7002172d14ed32b94df1dc6b07f4314`. Sesión `ba19e14b-a86a-4975-8739-8876245e35f1`; modelo reportado `claude-haiku-5-5`. Runner `gstack-claude-code --access read-only`, Read/Grep/Glob, exit0, respuesta no vacía. La sección siguiente preserva literalmente el resultado; es lectura estática declarada, no tests ni auditoría PR133. Proveedores/precios fueron NO_VERIFICADOS por Claude.

Se complementa la consulta parcial anterior conservada en v0.3: no se sustituye ni reetiqueta como la misma sesión. Dictamen nuevo: **IMP03: PROCEED_BOUNDED**, sujeto a C1–C11 y al cotejo de Work. IMP-01 conserva límites contractuales y no selecciona proveedor.

## CLAUDE CODE SAYS (consult)

```tool-output
# Revisión de arquitectura IMP-00/01 · EMERGENCY

**Base consultada:** HEAD `1703435` (rama `docs/implementacion-viva-20261127`), receptor observado `fa2381d`, candidato PR133 `e4d3f71` (declarado, no inspeccionado).
**Método:** solo lectura (Read/Grep/Glob). No ejecuté shell, pruebas ni builds. Donde no pude comprobar algo, lo marco como NO_VERIFICADO.
**Estado:** CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE. Esta revisión técnica no es liberación clínica ni aprobación del propietario.

---

## 1. Inventario verificable

### Operativo en el árbol actual (uso local, no productivo)

| Componente | Evidencia | Límite |
|---|---|---|
| PWA React/Vite/TS con build y tests (`npm test`, `npm run build`) | `app/package.json` L7–10 | `build` encadena generadores sin `--check` (`pediatrics:build`, `guides:build`, `procedures:build`, L7, L14–19). No verificado si escriben en archivos rastreados. |
| Motores deterministas en Python (calculadoras, ácido-base, scores, dosis) | `clinical/scripts/*.py` | Motores existentes; no se tocan en IMP-03. |
| API clínica local `clinical_note_api.py` (stdlib `http.server`) | `clinical/scripts/clinical_note_api.py` L735–745, L772 | Solo `127.0.0.1`/`localhost` (L737, L753–758). TLS opcional (L765–768). Sin autenticación de usuario. |
| Enrutado de 4 prefijos API en un proceso | `clinical_note_api.py` L544–562; `app/vite.config.ts` L52–56 | Los cuatro prefijos del proxy apuntan a 8765. |
| Perímetro loopback de proceso | `clinical/scripts/clinical_http_boundary.py` L1–5, L17–57 | Autentica un **proceso proxy**, no un médico. Token de 256 bits (L23). Exige Origin (L48) y Host exacto (L43–45). |
| Transporte acotado `BoundedHTTPServer` | `clinical/scripts/http_transport.py` L19–44, L64–124 | Deadline por lectura, semáforo de workers, TLS por hilo. Al saturarse, cierra la conexión sin 503 (L95–98). |
| Proxy Vite con inyección de token en Node | `app/scripts/clinical-api-boundary.mjs` L14–64 | Token solo en el proceso Node (L47–64). Borra el token enviado por el navegador (L39–40). |
| Launcher local compuesto | `scripts/run_local_review.py` L24–26, L40–56, L59–97 | Escritura atómica de recibos (L40–56) y parada de procesos (L82–97) reutilizables. |
| Almacenamiento en cliente | `app/src/lib/storage.ts` L1–16; `app/src/state/settings.tsx` L35–78 | localStorage solo para idioma, tema, unidades y contexto de referencia. No encontré persistencia de caso en código no-test (verificar). |
| CI con Sonar/Trivy/Semgrep, sin jobs de deploy | `.github/workflows/*.yml`; secretos `SONAR_TOKEN`, `PTBXL_BLINDING_SALT` | No hay `environment:` ni despliegue detectado. |

### Laboratorio (no entregable a usuario)

- **T05 (extracción OCR de gasometrías):** solo Windows, con Job Objects (`docs/LOCAL_REVIEW.md` L10, L13).
- **T06 (circuito sintético):** solo Linux (L11). Servidor propio en `127.0.0.1:8766` (`tools/t06-localhost-lab/lab/backend/server.py` L441).
- **Por tanto ningún SO ejecuta ambos adaptadores** (`docs/LOCAL_REVIEW.md` L13).
- **Vite dev con revisión local:** solo con `EMERGENCY_LOCAL_REVIEW=1` (`vite.config.ts` L18–21, L33–46). CSP de desarrollo con `unsafe-inline` (L44). El propio comentario dice que no es aislamiento de SO (L42–43).
- **Búsqueda externa de fuentes:** 8 fuentes HTTPS, cap de 5 MB. DNS rebinding **no** garantizado (`security/SECURITY_PERIMETER_REVIEW_2026-11-18.md` L7–9).

### No operativo / pendiente

- **Sin Dockerfile, compose, pyproject ni requirements raíz.** Solo `security/requirements-*` hash-locked, referenciados en `docs/LOCAL_REVIEW.md` L33, L47.
- **Sin script de backup, restore, rollback ni instalación** (búsqueda por nombre: solo `package.json` y launchers de laboratorio).
- **Sin identidad de usuario, OIDC, RBAC, sesiones ni BD.**
- **Sin gateway productivo.** `make_server` rechaza red (`clinical_note_api.py` L737–738).
- **MCP Emergency no localizado en este HEAD.** La búsqueda de `FastMCP`/`mcp.server`/JSON-RPC no dio resultados en código. Lo declarado (stdio, trusted-local, metadatos) no lo puedo verificar aquí.
- **PR133:** declarado en `ORQUESTACION.json` L8–41. No inspeccioné su diff.
- **DICOM y controles de búsqueda:** NOT_EXECUTED_POLICY_BLOCKED en navegador (`IMPLEMENTACION.md` L12).
- **LLM, RAG, PACS, FHIR, HL7:** no activados.

### Riesgos concretos al reutilizar componentes existentes

1. **Loopback no es frontera de confianza.** Cualquier proceso local del mismo usuario puede intentar conectar. El token vive en variable de entorno del proceso Node.
2. **Vite dev no es servidor de producción.** `npm run dev` y `vite preview` (`package.json` L6, L8) no deben formar parte del paquete.
3. **`BoundedHTTPServer` sin 503 al saturarse** (`http_transport.py` L95–98). El cliente ve un corte, no un error controlado.
4. **TLS es opcional** (`clinical_note_api.py` L765–768). Exponer HTTP plano por error es posible si se ignora la regla.
5. **`postinstall` modifica dependencias** (`package.json` L24: `picomatch-mitigation --apply`). Un `npm ci` sin `--ignore-scripts` lo ejecuta (`docs/LOCAL_REVIEW.md` L24 ya lo evita).
6. **Service Worker con `autoUpdate` y precache de `**/*.json`** (`vite.config.ts` L99–103, L123). Tras un rollback, un SW ya instalado puede seguir sirviendo el shell nuevo. Riesgo de incoherencia versión shell/API.
7. **Sin `runtimeCaching`** (L121–127): las respuestas `/api/*` no se cachean por SW. Bien. Mantener `navigateFallbackDenylist: [/^\/api\//]` (L126).
8. **Escritura atómica existe** (`run_local_review.py` L40–56). Reutilizable para pointer de versión.

---

## 2. Arquitecturas alternativas

Principio: el producto es **individual**. Un servicio remoto solo se justifica cuando exista una función que lo necesite (cuentas, sincronización, actualización de contenido firmado). Hospital, multicéntrico y RAG no bloquean esto.

### Arquitectura A — Local-first (recomendada para IMP-03/04)
- PWA compilada + API de cálculo en el dispositivo, `127.0.0.1`, datos de caso en memoria.
- Distribución por paquete versionado con manifiesto SHA-256 y rollback local.
- Sin cuenta: válido para uso de referencia local (`IMPLEMENTACION.md` L29).
- **Proveedores:** ninguno. Solo sistema operativo y Python 3.12/Node 22 declarados (`docs/LOCAL_REVIEW.md` L20).

### Arquitectura A+B — Local-first + gateway gestionado UE (recomendada cuando haya identidad)
- A para cálculo y datos de caso. Remoto solo para identidad OIDC, preferencias mínimas, auditoría técnica sin PHI y catálogos firmados.
- **Candidatos a verificar (NO_VERIFICADO: regiones, DPA, precios):**
  - **Cómputo:** Google Cloud Run en Madrid, ya citado en el repo (`IMPLEMENTACION.md` L21, L60; [regiones](https://docs.cloud.google.com/run/docs/locations), [precios](https://cloud.google.com/run/pricing)); Scaleway Serverless Containers ([pricing](https://www.scaleway.com/en/pricing/)); Azure Container Apps ([pricing](https://azure.microsoft.com/pricing/details/container-apps/)).
  - **PostgreSQL:** Scaleway Managed PostgreSQL; Supabase en región UE ([regiones](https://supabase.com/docs/guides/platform/regions), ya citado en el repo); Cloud SQL con región UE si la hay.
  - **Identidad:** Keycloak autogestionado ([keycloak.org](https://www.keycloak.org/)); gestionados: Microsoft Entra External ID ([docs](https://learn.microsoft.com/entra/external-id/)), Auth0 con tenant UE ([docs](https://auth0.com/docs)), Zitadel ([zitadel.com](https://zitadel.com)).
  - **Almacenamiento privado:** solo si aparece necesidad de artefactos remotos. Diferido.

### Arquitectura B — Contenedor gestionado UE (sin local)
- PWA estática + API ASGI en contenedor OCI en región UE, PostgreSQL gestionado, IdP OIDC gestionado.
- **Ventaja:** operación delegada. **Riesgo:** latencia, dependencia de red en guardia, coste variable, lock-in parcial.
- No cumple UX/offline por sí sola. Solo sirve si la cobertura offline se añade con la PWA.

### Arquitectura C — VPS europeo autogestionado
- Caddy (TLS automático, [docs](https://caddyserver.com/docs)) + Docker/Compose + PostgreSQL + Keycloak.
- **Proveedores (NO_VERIFICADO):** Hetzner Cloud ([hetzner.com/cloud](https://www.hetzner.com/cloud)), OVHcloud ([precios](https://www.ovhcloud.com/en/public-cloud/prices/)), Scaleway Instances.
- **Ventaja:** coste fijo bajo, control total. **Riesgo:** parches, backups, incidentes y disponibilidad recaen en el equipo. Mayor carga operativa.

### Variante D — Front estático en CDN + API separada
- Solo si mide mejora de distribución. No es requisito. Riesgo: orígenes distintos complican CSRF/CSP/cookies. Cualquier CDN de EE. UU. requiere DPA, subprocesadores y evaluación de transferencias.

**Descartado sin evaluar en detalle:** Kubernetes (sin necesidad medida), microservicios, colas múltiples, pgvector y bases vectoriales (sin función RAG aprobada).

---

## 3. Comparativa ponderada

Escala 1–5 (5 = mejor). **Juicio técnico, no medición.** Incertidumbre alta en TCO y plazo.

| Criterio (peso) | A Local-first | A+B Híbrida | B Gestionado UE | C VPS UE |
|---|---|---|---|---|
| Seguridad/fiabilidad (30%) | 4 | 4 | 4 | 3 |
| UX/offline (25%) | 5 | 4 | 3 | 3 |
| Carga operativa (15%) | 4 | 3 | 4 | 2 |
| TCO (15%) | 5 | 4 | 3 | 4 |
| Portabilidad (10%) | 4 | 4 | 4 | 4 |
| Plazo (5%) | 4 | 3 | 3 | 2 |
| **Ponderado** | **4,40** | **3,80** | **3,55** | **3,05** |

**Justificación:**
- **A (4 en seguridad):** superficie remota mínima, sin PHI remoto. No es 5 porque el dispositivo es el punto de confianza: pérdida, equipo compartido e integridad del cliente son riesgos reales.
- **A+B (4 en seguridad, 3 en operación):** una identidad y una BD mal configuradas son más riesgo que la ausencia de ambas. El peso de la operación crece con dos superficies.
- **B (3 en UX):** depende de red en guardia.
- **C (2 en operación):** parches, backups y disponibilidad son responsabilidad propia.

**Incertidumbre:** TCO y plazo tienen incertidumbre alta. El resultado cambia si la función de identidad o sincronización pasa a ser obligatoria.

---

## 4. Escenarios 10 / 100 / 1000 médicos activos

**Todo es hipotético.** Los parámetros son supuestos de modelado, no datos observados.

**Supuestos (HIPÓTESIS):**
- `D` = médicos activos.
- `a` = 0,4 fracción activa diaria.
- 20 sesiones/médico activo/día; 10 llamadas API por sesión en el escenario remoto hipotético → 200 llamadas por médico activo/día.
- Respuesta media 20 KB.
- Hora punta = 15 % del tráfico diario.
- Latencia media W = 0,3 s.
- Factor de pico ×3 para ráfagas.
- 50 eventos de auditoría técnica/médico activo/día, 1 KB cada uno, retención 365 días.

**Fórmulas:**
- Llamadas/día = `D · a · 200`
- Pico (rps) = `Llamadas/día · 0,15 / 3600 · 3`
- Concurrencia (Little) = `λ · W`
- Egreso/mes = `Llamadas/día · 20 KB · 30`
- Almacenamiento de auditoría/año = `D · a · 50 · 1 KB · 365`

| Escenario | Llamadas/día | Pico (rps, con ×3) | Concurrencia (L) | Egreso/mes | Auditoría/año |
|---|---|---|---|---|---|
| 10 médicos | 800 | ~0,1 | ~0,03 | ~0,5 GB | ~73 MB |
| 100 médicos | 8 000 | ~1 | ~0,3 | ~4,8 GB | ~0,7 GB |
| 1000 médicos | 80 000 | ~10 | ~3 | ~48 GB | ~7,3 GB |

**Costes (estructura, sin importes):**
- `C_mes = c_cómputo + c_BD + c_backup + c_almacenamiento + c_egreso + c_IdP + c_observabilidad + c_IA + h_operación · r_hora`
- **c_IdP:** depende de MAU si el proveedor cobra por MAU. MAU ≈ `D` (HIPÓTESIS). Muchos IdP tienen umbrales gratuitos; verificar.
- **c_IA:** 0 en esta fase (LLM desactivado). Si se activa: `llamadas · tokens · precio/token`. Precio NO_VERIFICADO.
- **Horas de operación (HIPÓTESIS):** A ≈ 4 h/mes; A+B ≈ 12 h/mes; B ≈ 16 h/mes; C ≈ 30 h/mes.
- **Redundancia (HIPÓTESIS):** 1 instancia para 10 y 100 médicos; 2 para 1000 (alta disponibilidad mínima).

**Precios: NO_VERIFICADO.** Work aportará tarifas oficiales comprobadas. No tomar cifras de este documento.

**Lectura técnica:** a 1000 médicos el tráfico es pequeño (~10 rps pico). La carga la dominan el coste de operación y la identidad, no el cómputo. La opción local tiene el coste más bajo en todos los tramos porque no genera egreso.

---

## 5. Modelo de amenazas y casos negativos

| Riesgo | Control propuesto | Caso negativo (prueba) |
|---|---|---|
| Servidores de desarrollo expuestos (Vite dev, `preview`) | Excluir `dev`/`preview` del paquete. Bind `127.0.0.1` obligatorio (`clinical_http_boundary.py` L18–19) | Bind a `0.0.0.0` → `ValueError`. Host ajeno → 403 (`vite.config.ts` L84–88) |
| Aislamiento entre usuarios | Identidad por `(issuer, subject)`; autorización en cada recurso | Usuario A pide recurso de B → 404 |
| OIDC | Authorization Code + PKCE; state, nonce, `iss`, `aud`; alineado con RFC 9700 (fuente en `IMPLEMENTACION.md` L60) | Sin PKCE, state distinto, `aud` ajeno, token expirado → rechazo |
| MFA | Delegado al IdP; no inventar MFA propio | Política exigida sin claim de MFA → rechazo |
| CSRF | `Origin` + `Sec-Fetch-Site` (`clinical_http_boundary.py` L42–49); cookies SameSite | POST con Origin ajeno → 403 |
| XSS | CSP estricta sin `unsafe-inline` en producción (`vite.config.ts` L44 es solo dev) | Texto inyectado en nota se renderiza como texto; violación CSP registrada |
| SSRF | Sin fetch de URL proporcionada por el usuario. Surveillance fuera de la API | `169.254.169.254`, `127.0.0.1`, DNS privado → rechazo (`SECURITY_PERIMETER` L7–9). Rebinding residual documentado |
| Egress de la API | Allowlist de salida por firewall/proxy | Proceso API conecta a host arbitrario → bloqueado |
| Caché offline | Precache SW solo del manifiesto; sin `runtimeCaching` para `/api` | Tras logout, no se sirven respuestas autenticadas cacheadas |
| Logs | Sin request-line ni cuerpos (`clinical_note_api.py` L729–732) | Marcador sintético en nota → 0 coincidencias en logs |
| Exportaciones | Solo las que pide el usuario; temporal borrado tras descarga | Export no queda en disco del servidor tras descarga |
| Pérdida de dispositivo | Caso en memoria; sin persistencia de caso (verificar) | Tras cierre, sin datos de caso en localStorage/IndexedDB |
| Equipo compartido | Logout borra sesión y cachés autenticadas | Segundo usuario no accede a datos del primero |
| Fallo del IdP | Modo local sigue operativo. Remoto degrada explícitamente | IdP caído → cálculo local funciona; no hay acceso anónimo remoto |
| Cadena de suministro | `npm ci --ignore-scripts`; manifiesto SHA-256; firma en IMP-07; SBOM | Archivo alterado → instalación rechazada. Versión sin manifiesto → rechazo |
| Rollback | Versión N-1 conservada; puntero atómico | Corte durante conmutación → versión previa activa. Hash N-1 incorrecto → rechazo |
| Incoherencia SW tras rollback | Versionar SW por build; limpiar caches en activación | Rollback en navegador real (Playwright, ya en devDeps) sirve shell N-1 |
| RAG/IA: derechos y fugas | LLM desactivado; permisos por fuente; `LOCAL_CUSTODY_ONLY` no indexado (`IMPLEMENTACION.md` L30) | Consulta de `LOCAL_ONLY` no devuelve contenido. Prompt injection en fuente → sin efecto |
| Pérdida de datos remotos | Backup cifrado separado; restore periódico | Restore a BD vacía reproduce esquema y conteos |

---

## 6. ADR propuestas

Estado de todas: **PROPUESTO**. No aceptadas.

**ADR-001 · Empaquetado local con manifiesto y pointer atómico**
- **Context:** IMP-03 pide instalación, actualización y rollback reproducibles, sin remoto.
- **Decision:** artefacto por versión en directorio propio (`releases/<revision>-<digest>/`), manifiesto SHA-256 por archivo, puntero `current.json` escrito con el patrón de `run_local_review.py` L40–56.
- **Alternatives:** symlink (requiere privilegio en Windows); Docker Desktop (dependencia pesada); Electron/Tauri (fuera de alcance, cambia el producto).
- **Consequences:** sin firma de confianza en esta fase; detecta corrupción, no manipulación con acceso de escritura.
- **Dependencies:** IMP-00 (esta revisión, a registrar por Work).
- **Verification:** tests de manifiesto alterado, corte durante conmutación, rollback N-1, `npm test` y `npm run build` observados.

**ADR-002 · Puerta de API productiva: adaptador ASGI sobre router puro**
- **Context:** `BoundedHTTPServer` y el handler de `clinical_note_api.py` no son gateway público (sin TLS obligatorio, sin autenticación, sin 503).
- **Decision:** extraer del handler una función pura `dispatch(método, ruta, cuerpo) → (estado, json)` sin cambiar salidas. Montarla en un adaptador ASGI (Starlette/FastAPI como candidatos a verificar) detrás de proxy TLS.
- **Alternatives:** exponer `BoundedHTTPServer` con TLS (descartado); reescribir motores (descartado).
- **Consequences:** exige pruebas doradas byte a byte antes y después.
- **Dependencies:** IMP-04 depende de IMP-00 e IMP-01 según cola. IMP-02 no es dependencia de IMP-04 en la cola.
- **Verification:** tests dorados de salidas idénticas; contratos negativos (métodos, tamaños, tiempos, Host ajeno); sin puerto de desarrollo expuesto.

**ADR-003 · Identidad OIDC Authorization Code + PKCE, proveedor no elegido**
- **Context:** no hay identidad hoy. Solo se necesita si hay función remota.
- **Decision:** OIDC con sesión de servidor, cookies `Secure; HttpOnly; SameSite=Strict`. Proveedor pendiente de elección entre Keycloak autogestionado y gestionado UE.
- **Alternatives:** tokens de larga duración en navegador (descartado); anonimato con claves (descartado).
- **Consequences:** dependencia de IdP; mitigable con modo local.
- **Dependencies:** IMP-01, IMP-02 y IMP-04 según cola (IMP-05 exige los tres).
- **Verification:** `iss`/`aud`/`nonce`/`state`, PKCE obligatorio, sesión revocada tras logout, IdP caído no abre acceso anónimo.

**ADR-004 · PostgreSQL mínimo para cuentas, preferencias y auditoría técnica**
- **Context:** IMP-06 necesita persistencia mínima. No hay historia clínica remota.
- **Decision:** tablas de identidad, preferencias y auditoría sin contenido clínico. Migraciones expand/contract.
- **Alternatives:** SQLite local-first (válido para preferencias en A); BD vectorial (descartado sin función RAG).
- **Consequences:** backup y restore obligatorios antes de usarla.
- **Dependencies:** IMP-01, IMP-02 y IMP-04 según cola.
- **Verification:** restore a BD vacía; aislamiento por usuario en consulta; ningún campo clínico libre.

**ADR-005 · Infraestructura declarativa sin Kubernetes**
- **Context:** IMP-07 pide staging parametrizado sin gasto.
- **Decision:** plantillas OpenTofu en dry-run local; un contenedor OCI por servicio; sin orquestador.
- **Alternatives:** Kubernetes (sin necesidad medida); VPS manual (menos reproducible).
- **Consequences:** escalado vertical hasta medir necesidad.
- **Dependencies:** IMP-04, IMP-05, IMP-06.
- **Verification:** `plan` sin recursos creados; restore y rollback documentados y probados en local.

**ADR-006 · RAG y vector DB diferidos**
- **Context:** RAG y modelos externos son candidatos, no validados (`docs/ARCHITECTURE.md` L33).
- **Decision:** ningún componente RAG en IMP-03–07. Sin pgvector.
- **Dependencies:** evaluación clínica separada; IMP-02 para derechos de fuente.
- **Verification:** cuando se proponga, criterio de evaluación independiente.

---

## 7. Dictamen IMP-00

**¿Puede Codex iniciar ya IMP-03?** **Sí, de forma acotada.**

**Alcance mínimo útil de IMP-03:**
1. Script de empaquetado que construye la PWA con `npm ci --ignore-scripts` y genera manifiesto SHA-256 (`scripts/package_local.py`, nuevo).
2. Instalación en `releases/<revision>-<digest>/` con verificación previa a la conmutación.
3. Conmutación atómica del puntero `current.json` (patrón de `run_local_review.py` L40–56).
4. Rollback a la versión N-1 con verificación de hash.
5. Servidor estático stdlib en `127.0.0.1` con CSP de producción (`vite.config.ts` L44, sin `unsafe-inline`) y solo archivos del manifiesto.
6. API clínica existente (`clinical_note_api.py`) arrancada en loopback con token de sesión generado en cada arranque.
7. Pruebas de manifiesto alterado, corte durante conmutación, rollback, traversal, archivo fuera de manifiesto, bind no loopback, ausencia del token en `dist/`.

**Condiciones de seguridad exactas:**
- **C1.** Bind solo `127.0.0.1` / `localhost`. Reutilizar la validación de `make_server` (`clinical_note_api.py` L737–738) y `configure_local_server` (`clinical_http_boundary.py` L18–19).
- **C2.** Token de sesión generado con `secrets.token_hex(32)` por arranque. Nunca en `dist/`, nunca en `VITE_*`, nunca en recibos.
- **C3.** Sin `npm run dev` ni `vite preview` en el paquete. Sin `sourcemap` salvo `auditBuild` (`vite.config.ts` L32).
- **C4.** Servidor estático: rechazo de traversal, listado de directorio y archivos fuera del manifiesto. Cabeceras `nosniff`, `no-referrer`, `no-store`, CSP estricta.
- **C5.** Conmutación atómica. Un fallo deja la versión previa activa.
- **C6.** Instalación sin red en tiempo de ejecución. La descarga de modelo OCR queda fuera.
- **C7.** Versionado del Service Worker por build y limpieza de cachés al activarse, para evitar shell N-1 tras rollback. Verificar con Playwright (ya en devDeps).
- **C8.** Sin datos reales. Solo fixtures sintéticos. Recibo con marca `synthetic-only`.
- **C9.** No modificar motores, `drugs.json`, módulos clínicos ni dosis. Verificar por hash antes y después.
- **C10.** Ningún proceso de T05/T06 entra en el paquete por defecto. El paquete declara sus capacidades, como hace `--check` (`docs/LOCAL_REVIEW.md` L59).
- **C11.** Base de trabajo: receptor `fa2381d`. PR133 solo como evidencia, salvo que el propietario decida integrarlo.

**Necesidad arquitectónica material faltante:** ninguna que bloquee IMP-03. La firma de artefactos (trust root) no es necesaria aquí: el manifiesto basta para integridad local. Queda para IMP-07.

**Dependencias:** IMP-03 en la cola depende solo de IMP-00. Work debe registrar esta entrega como recibo antes de que Codex inicie. No lo inferí como hecho.

---

## 8. Implementación progresiva IMP-03..07

**Principio:** cada incremento reutiliza lo existente. Sin Kubernetes. Un proceso Python por servicio, proxy TLS delante cuando haya exposición.

| Incremento | Ficheros reutilizables | Nuevos | Pruebas | Límite de dependencia |
|---|---|---|---|---|
| **IMP-03** local | `run_local_review.py` (L40–97), `clinical_http_boundary.py`, `http_transport.py`, `vite.config.ts`, `check-pwa-offline.mjs`, `check-lab-exclusion.mjs` | `scripts/package_local.py`, `scripts/serve_local_package.py` | Unit de manifiesto/conmutación/rollback; traversal; bind; token ausente en `dist/`; `npm test`, `npm run build` | No importa T05/T06 ni red |
| **IMP-04** gateway | `clinical_note_api.py` (extraer `dispatch`), `http_transport.py` | `gateway/` (adaptador ASGI) | Dorados byte a byte; negativos de método, tamaño, tiempo, Host; sin puerto dev | Gateway importa motores, no al revés |
| **IMP-05** OIDC | `clinical_http_boundary.py` (patrón de Origin/Sec-Fetch-Site) | Middleware OIDC, cliente de sesión | Proveedor sintético; state/PKCE/nonce; cruce de cuentas; revocación | Solo capa de identidad; sin lógica clínica |
| **IMP-06** BD | — | Esquema mínimo, migraciones | Restore a BD vacía; aislamiento por usuario; sin campos clínicos | Solo metadatos no clínicos |
| **IMP-07** staging | `security/` CI existente | Plantillas OpenTofu, runbooks, backups | Dry-run sin recursos; restore sintético; rollback documentado | Sin gasto ni nube real |

**Límites de dependencia:**
- Motores clínicos no importan gateway, identidad ni BD.
- `security/` (surveillance, egress) no se importa desde la API.
- T06 no entra al paquete.
- Frontend solo llama a `/api/*` del mismo origen.

**Pruebas adecuadas:** tests unitarios de manifiesto y conmutación; dorados de salida de API; negativos de seguridad por riesgo (sección 5); navegador con Playwright para SW y rollback; `npm test`, `npm run build`, `npm run check:lab-exclusion`, y las verificaciones clínicas del `CLAUDE.md` del repo solo si se toca clínico.

---

## Cinco decisiones materiales

1. **¿Fase 1 sin cuentas remotas y OIDC solo cuando exista función remota?** Recomendación: **sí**. Reduce superficie sin afectar uso individual.
2. **¿Proveedor de cómputo, BD e IdP?** Recomendación: **diferir** hasta cerrar IMP-02. No seleccionar ahora.
3. **¿Retención de auditoría técnica sin PHI?** Recomendación: **30 días** de logs operativos y **365 días** de auditoría de acceso sin contenido clínico. Validar con IMP-02.
4. **¿Firma de artefactos ahora o en IMP-07?** Recomendación: **manifiesto SHA-256 en IMP-03; firma en IMP-07** con clave gestionada fuera del repo.
5. **¿Excluir T05/T06 del paquete individual?** Recomendación: **sí**. Son laboratorio, requieren plataformas distintas y no deben presentarse como capacidades entregables.

---

## Hallazgos priorizados

**P0 (bloquean exposición remota, no IMP-03):**
- **P0-1.** No hay autenticación de usuario ni autorización por usuario. `clinical_http_boundary.py` L1–5 autentica un proceso, no un médico. Bloquea cualquier exposición. Se resuelve en IMP-05.
- **P0-2.** La API Python no exige TLS (`clinical_note_api.py` L765–768). Ninguna exposición sin proxy TLS.

**P1 (resolver antes de IMP-04/05):**
- **P1-1.** Incoherencia SW tras rollback (`vite.config.ts` L99–103). Mitigación en C7.
- **P1-2.** `npm run build` encadena generadores sin `--check` (`package.json` L7). Verificar que no mutan archivos rastreados antes de empaquetar.
- **P1-3.** `postinstall --apply` muta dependencias (`package.json` L24). Usar `--ignore-scripts` como indica `docs/LOCAL_REVIEW.md` L24.
- **P1-4.** `BoundedHTTPServer` cierra sin 503 al saturarse (`http_transport.py` L95–98). Requiere respuesta controlada en el gateway.
- **P1-5.** Ningún SO ejecuta T05 y T06 a la vez (`docs/LOCAL_REVIEW.md` L13). El paquete no puede prometer ambos.
- **P1-6.** DNS rebinding no garantizado en surveillance (`SECURITY_PERIMETER` L9). Mantener sin red en la API.
- **P1-7.** No hay backup/restore/rollback de datos. Obligatorio antes de IMP-06.
- **P1-8.** MCP Emergency no localizado en HEAD. No puedo verificar su superficie.

**P2 (mejora):**
- **P2-1.** Dependencias Python sin lock raíz. Solo `security/requirements-*`.
- **P2-2.** `vite preview` y `dev` documentados sin aclarar que no son producción.
- **P2-3.** Confirmar en código no-test que ningún caso clínico se persiste en localStorage/IndexedDB.

**Acuerdos con el plan `IMPLEMENTACION.md`:** modo local sin cuenta, separación de capas, RPO/RTO de metadatos y firma en IMP-07. Ninguno requiere cambio.

**Objeciones al plan:** el plan menciona Cloud Run Madrid como candidato. Está bien como candidato, pero el coste y la dependencia no se miden aquí. Work debe compararlo con las alternativas de la sección 2.

---

**Estado de verificación de esta revisión:** lectura de archivos y búsquedas. Pruebas no ejecutadas. Precios, regiones y DPA NO_VERIFICADOS. PR133 declarado, no inspeccionado. MCP no localizado.

ARCHITECTURE_REVIEW: DELIVERED
IMP03: PROCEED_BOUNDED
```

## Cotejo de Work

Autor de este apartado: Work/Codex. No forma parte de la respuesta de Claude.

- SHA256 detects corruption only; a replaceable manifest is not publisher authenticity. Local artifact requires separately trusted expected digest and controlled custody. Signing/trust-root remains mandatory before untrusted distribution.
- TLS optional and missing end-user authentication are conditions blocking remote exposure, not proven vulnerabilities in the deliberately loopback-only current service.
- C7 requires same-origin browser/cache verification. HTTP no-store alone does not remove an already controlling Service Worker; clearing unrelated browsing data is not authorized.
- A static reference-only package with API503 may be a useful subdelivery; it does not satisfy the clinical-API launcher step or prove equivalence of all clinical workflows.
- Cookie SameSite=Strict is a proposal, not accepted OIDC configuration. Cross-site callback and transaction-cookie behavior require explicit tests; do not copy it uncritically.
- Historical surveillance DNS statements were not independently reproduced against its current implementation; retain as historical scoped uncertainty.
- The proposed retention periods, provider choice and exclusion of optional capabilities remain proposals; preserve prior owner decisions and do not ask duplicate approvals.

La tabla ponderada se recalculó: A4,40; A+B3,80; B3,55; C3,05. Los cuatro resultados coinciden; son juicios hipotéticos, no benchmarks. Los escenarios de carga de Claude y el ejemplo tarifario separado de Work usan supuestos distintos y no deben mezclarse.

# Comprobación primaria adicional de Work/Codex

Consulta web real del 27/11/2026. Material separado de la respuesta de Claude: no atribuirle estas búsquedas ni presentar una tarifa como gasto real o TCO completo. No se ha creado cuenta, contratado ni provisionado nada.

## Tarifas verificadas y límites

- [Scaleway Serverless, París](https://www.scaleway.com/en/pricing/serverless/): €0,00001/vCPU-s y €0,000002/GB-s; franquicias mensuales por cuenta 200.000vCPU-s y 400.000GB-s. Mantener instancia caliente consume recursos. Impuestos, red y otros productos no se deducen de ese cálculo.
- [Scaleway PostgreSQL/MySQL](https://www.scaleway.com/en/pricing/managed-databases/): París, DB-DEV-S €0,0156/h; DB-PRO2-XXS €0,11/h; bloque5K €0,0993/GB/mes; copias/snapshots €0,03/GB/mes. Los nombres DEV y PRO no demuestran por sí solos adecuación, disponibilidad o capacidad. El subtotal debe incluir almacenamiento, copias y modalidadHA elegida; no presume nodo adicional.
- [Scaleway Object Storage, París](https://www.scaleway.com/en/pricing/storage/): StandardMultiAZ €0,01606/GB/mes; OneZone €0,00803/GB/mes; salida75GB/mes incluidos y después €0,01/GB; entrada y peticiones incluidas según tabla publicada. Cargos mínimos por unidad iniciada y reglas regionales: revisar antes de compra. No se admiten imágenes de pacientes ni fuentes restringidas.
- [ZITADEL tabla detallada](https://zitadel.com/pricing/detail): Free100DAU; Pro baseUS$100/mes, tabla25.000DAU incluidos. La calculadora utiliza usoDAU en el período y no define inequívocamente en el extracto si coincide con promedio diario o acumulación mensual: confirmar unidad contractual; no tratarMAU comoDAU. Sin tarifa de conversiónUSD/EUR ni impuestos supuestos. Free no ofrece el mismo compromiso de disponibilidad; precios de dominio, soporte/SLA y otros extras separados.
- [Google Cloud Run](https://cloud.google.com/run/pricing): lista Madrid/europe-southwest1. La tabla dinámica publicada muestra CPU activaUS$0,000024/vCPU-s, memoriaUS$0,0000025/GiB-s y US$0,40/millónpeticiones. La extracción no acredita que la región seleccionada de la tabla fuera Madrid: **no se usa como cotización regional ni subtotal**. CloudSQL,red,IdP y soporte separados.
- [Hetzner página de ajuste](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/): buscador devolvió tarifas actualizadas2026, pero apertura directa devolvió404. **Tarifa no verificada por lectura directa; no usar cantidades en comparación final**. No sustituir la fuente original por blog o caché de terceros.

## Condiciones de tratamiento

- [Scaleway contratos](https://www.scaleway.com/en/contracts/) publica DPA y medidas técnicas; [subencargados](https://www.scaleway.com/en/subprocessorlist/) identifica proveedores por producto y ubicación. Proveedor europeo o infraestructuraUE no eliminan revisión contractual por servicio, soporte, terceros o transferencia. No hay aceptación ni evaluación legal final en esta consulta.
- [Hetzner protección de datos](https://docs.hetzner.com/general/company-and-policy/data-protection-at-hetzner/) indica DPA concluyente desde cuenta y especificidades por productos/regiones. No abrir cuenta ni considerar el acuerdo firmado por consultar la página.
- [ZITADEL DPA](https://zitadel.com/docs/legal/data-processing-agreement), actualizado8/05/2025, permite procesamiento fueraSuiza/UE/EEE sujeto a salvaguardas/SCC. El documento muestra dos cláusulas con plazos de objeción distintos,5y15días: aclaración contractual pendiente. Residencia de almacenamiento elegible no significa tratamientoEU-only. [Lista oficial](https://zitadel.com/docs/legal/subprocessors) remite alTrustCenter; lista íntegra contractual no recuperada aquí.

## Documentación técnica de identidad

Context7 consultado realmente: biblioteca `/websites/zitadel` (reputaciónHigh), tema authorizationcode/PKCE/BFF,Python; devuelve [endpoints oficiales](https://zitadel.com/docs/apis/openidoauth/endpoints). Confirma intercambio de código con redirectURI exacta y code_verifier en PKCE, métodos confidentialclient y renovación; no certifica seguridad de una implementación inexistente. No se copiaron ejemplos con credenciales aparentes al código.

## Modelo reproducible y no medido

`calcular_costes.py` declara todas las hipótesis y produce `COSTES_ESCENARIOS_WORK.json`. Compara10/100/1.000médicos con20díasactivos,20peticionesremotas/día,0,2CPU-s y0,1GB-s/petición,0,06GB/usuario/mes de salida. Supone10GB de objetos,20GB de DB y60GB de copias. El cálculo sinfranquicias y confranquicias se separa; no modela latencia,coldstart,concurrenciaefectiva,correo/MFA,SLA,logs,CI,escáner,dominio,LLM ni otros cargos. El subtotal técnico no es TCO ni presupuesto aprobado. Sin IA remota en esta fase.


## Custodia y siguiente acción

Respuesta, JSON original del runner, cotejo, fuentes y cálculo reproducible quedan bajo `ChatGPT_Trabajo/IMPLEMENTACION_20261127/EVIDENCIAS/CLAUDE/`. Work registra recibos en la cola única y puede ejecutar el incremento local acotado; no supone aceptación de los ADR, contratación, exposición pública ni liberación. `CLINICALLY_PENDING` · `NO_GO_CLINICAL_RELEASE`.
