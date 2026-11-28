# IMP-01 · decisión técnica residual entregada

27/11/2026. Base de consulta `63f4d4d10b3325b62dc8975992896ca462f9f920`; PR134 `26be61a` y PR135 `8699cdc` conservadas. Sesión Claude Code real `ba19e14b-a86a-4975-8739-8876245e35f1`, continuada con herramientas de solo lectura; modelo comunicado: claude-haiku-5-5. Exit 0, respuesta no vacía de 12454 caracteres. No ejecutó pruebas ni consultó precios web; no auditó el código que se implementaba en paralelo.

**Resultado para aceptación de Work:** local primero, PWA existente más Python empaquetado y versiones acopladas; híbrida remota escalable opcional. No quedan decisiones de arquitectura que obliguen a detener IMP-03 local. Cuentas remotas, OIDC, PostgreSQL y objetos no son prerrequisitos de ese modo. Proveedor/contrato/gasto/despliegue quedan sin seleccionar ni autorizar. El responsable de Work acepta el alcance técnico; esto no es una aceptación médica.

[ADR residuales](ADR_RESIDUALES.json) conserva condiciones y criterios de aceptación. No añade tareas a los doce IDs. Los modelos de 10/100/1.000 médicos siguen siendo hipótesis documentadas: repartir cálculo entre dispositivos no equivale a TCO cero; cotización, capacidad y costes regionales remotos se comprueban si se elige esa capacidad.

## CLAUDE CODE SAYS (consult)

```tool-output
# IMP-01 · decisión técnica residual: modo local primero

Base: `63f4d4d` (composición aislada PR135 `8699cdc` + referencia PR134 `26be61a`), receptor `fa2381d`. PR129–133 sin integrar. No dictamino que la implementación concurrente de `tools/local-installation` esté terminada ni auditada; esta decisión no depende de su estado. Lectura documental y de código; sin pruebas ejecutadas. Estado: CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE. Esto no es aprobación clínica ni jurídica.

## 1. Arquitectura principal (v1 individual)

- **Paquete local verificado:** PWA compilada existente + motores Python existentes, sin cambios en dosis, motores ni reglas.
- **Launcher local** (proceso del usuario, `127.0.0.1` únicamente):
  - Servidor estático que sirve la PWA en un **puerto fijo configurado** (no uno nuevo por arranque).
  - Proxy `/api/*` hacia la API clínica en un puerto interno distinto. El token se inyecta en el servidor, nunca en el navegador. Mismo patrón que `app/scripts/clinical-api-boundary.mjs` L47–64.
- **Episodios:** estado en memoria de la PWA. Exportaciones generadas en directorio temporal del usuario, entregadas y borradas. Sin persistencia de caso.
- **Preferencias:** `localStorage` con esquema versionado y validado (idioma, tema, unidades, contexto de referencia; ya existen en `app/src/state/settings.tsx` L35–78 y `app/src/context/reference-context.ts` L32). No requiere base de datos.
- **Sin red:** CSP `connect-src 'self'`, sin telemetría ni llamadas externas.
- **Excluidos de v1:** T05 (OCR), T06, LLM/cloud, surveillance, MCP, RAG, DICOM. Declararlos como capacidades no empaquetadas.

**Condiciones de cierre técnico (no clínicas):**
1. Bind solo loopback. Si un puerto está ocupado, el arranque falla sin terminar procesos ajenos (regla de `docs/LOCAL_REVIEW.md` L59).
2. Host y Origin exactos; `Sec-Fetch-Site` acotado; solo JSON; límite de tamaño (`http_transport.py` L19–44); deadline por petición (L64–75).
3. Saturación responde **503 JSON**, no cierre silencioso (corrige `http_transport.py` L95–98, P1).
4. Token de 256 bits por arranque; vive solo en memoria del launcher y en el entorno de los hijos. No aparece en `dist/`, recibos, logs ni storage.
5. `build_id` común a estático y API. La API responde **409** a cabeceras `X-Emergency-Build` distintas: cliente obsoleto rechazado.
6. Allowlist de rutas generada desde la tabla real de `clinical_note_api.py` (L544–562, L678). Quedan fuera blood-gas (8767) y T06 (8766).

## 2. Cuándo no hacen falta servidor remoto, OIDC, usuarios remotos, PostgreSQL ni objetos

| Necesidad | ¿Requerida en v1 local? | Motivo |
|---|---|---|
| Servidor remoto | No | Cálculo y episodio en el dispositivo. Descarga de paquete es opcional. |
| OIDC / identidad profesional | No | No hay función remota ni datos remotos. |
| Usuarios remotos | No | Sin cuentas ni sincronización. |
| PostgreSQL | No | Tres preferencias no justifican una BD. |
| Almacenamiento de objetos | No | Paquete local; no hay artefactos remotos. |

**Identidades, distinguidas:**
- **Token del launcher:** autentica el proceso BFF↔API y la sesión local. **No identifica al médico.**
- **Cuenta del sistema operativo:** es el único límite real de acceso a ficheros del paquete y temporales. Dos personas con la misma cuenta de SO no están aisladas.
- **Consecuencia:** v1 **no es multiusuario**. Un proxy loopback tampoco lo es. Un equipo compartido exige bloqueo, cierre y borrado de temporales por el SO.

## 3. Alternativa híbrida preparada (no implementada)

**Preparado ahora, solo como contrato:**
- Mismo BFF que podría subir a un contenedor, sin importar el launcher.
- `api_version`, `build_id` y esquema de preferencias v1 versionados.
- Exportación portable de preferencias en JSON.

**No se incorpora ahora:** gateway público, OIDC, PostgreSQL, objetos, IaC, LLM, vector DB, servicios hospitalarios.

**Disparadores medibles (propuestos):**
- T1: sincronización entre dispositivos aprobada por el propietario.
- T2: más de un dispositivo por médico, con requisito funcional demostrado.
- T3: tasa de fallo de instalación o actualización **> 5 %** en 30 días sobre instalaciones reales (umbral propuesto, no medido).
- T4: obligación contractual de auditoría remota.
- T5: licencia o suscripción que exige verificación en línea.

Si se activa un disparador, la preferencia operativa provisional es **contenedor OCI gestionado en UE**. VPS solo si hay capacidad real de mantenimiento. Ningún proveedor queda elegido.

**Salida y portabilidad:** OCI estándar, PostgreSQL estándar, OIDC estándar y JSON de preferencias. Sin lock-in en el código.

## 4. Costes y escala

**Local:**
- Cálculo en dispositivo: **cero carga central por médico**. No equivale a TCO cero.
- Reservas de horas (de `CLAUDE_COMPARATIVA`/cotejo, hipótesis): A 2/3/6 h/mes para 10/100/1.000. Con 40 EUR/h: 80/120/240 EUR. No se suman a USD sin tipo de cambio fechado.
- Descarga de actualizaciones (modelo de hipótesis 10 MB/médico/mes): 0,10 / 1,00 / 10,00 GB/mes. Si se usa alojamiento estático, la referencia verificada por Work da 0 / 0 / 0,75 USD de exceso. Solo referencia.

**Remoto (solo si se elige):** del cotejo de Work, subtotal de referencia no es factura:
- B (SQL de referencia + Run bruto + OIDC): 103,71 / 104,76 / 121,20 USD + ΔSQL-UE + extras.
- D: 57 USD o 80 USD según sensibilidad.
- C: 20 / 20 / 35 EUR como sobre de planificación, no tarifa.

**Requieren cotización solo si se elige esa capacidad:**
1. Tarifa SQL exacta de la región UE contratada.
2. Tarifa de identidad por MAU del producto y región elegidos.
3. Tarifa de cómputo de la región concreta (Madrid no quedó confirmada en la tabla extraída).
4. Red/egress de cómputo y conectores.
5. Unidad DAU/MAU de ZITADEL y cláusula de objeción del DPA.
6. Stock, configurador y opción de copia del VPS.
7. Retención de backups y PITR.
8. Dominio, correo/SMS/MFA, logs, IVA y FX.

**Local no requiere cotización** salvo que se contrate un canal público de descarga.

**Escala local:** 10, 100 o 1.000 médicos no cambian la carga central, porque no hay servidor central en la ruta de cálculo.

## 5. Seguridad y mantenimiento local

- **Actualización explícita, sin perder episodio:** no hay actualización automática. Si hay un episodio activo, la actualización queda pendiente. Se ofrece al cerrar o exportar. Reiniciar el launcher pierde el episodio en memoria; esto debe mostrarse antes de actualizar.
- **Origen estable:** puerto fijo. Las preferencias sobreviven a actualizaciones y rollbacks en el mismo origen. **Tensión:** el candidato PR135 usa origen nuevo por arranque (`RESULTADO_LOCAL.md` L36), lo que pierde preferencias. Recomiendo origen estable y verificar coherencia del Service Worker con Playwright. Si esa prueba falla, la alternativa es documentar la pérdida de preferencias.
- **Coherencia UI/API:** `build_id` y rechazo 409 (ver §1.5).
- **Sesión/token:** solo en servidor. Nunca en el navegador ni en `VITE_*`.
- **Host/Origin/CSRF:** exactos, con `Sec-Fetch-Site` y JSON obligatorio. Host ajeno (rebinding) → 403.
- **Firma:** un SHA-256 de manifiesto no autentica al editor. Propongo **firma Ed25519 sobre el manifiesto canónico**, con clave pública fijada en el launcher, identificador de clave y contador mínimo de versión (anti-rollback). Tests con clave de prueba claramente separada. Rechazar: archivo alterado, manifiesto reescrito, clave desconocida, versión revocada.
- **Trazabilidad:** un recibo por instalación, actualización y rollback (hash, UTC, resultado), sin PHI.
- **Pérdida de dispositivo:** solo se persisten paquetes y preferencias. Cifrado de disco (BitLocker/FileVault) es requisito del equipo, no verificado por la app.
- **Reutilización del backend:** `dispatch`/rutas permitidas sin cambiar salidas. Los motores no cambian.
- **Dependencias Python:** la API requiere Python 3.12 instalado. Hay que fijar dependencias con hashes. **NO_VERIFICADO:** si los motores usados solo importan stdlib.

## 6. ADR residuales

| ID | Decisión principal / alternativa | Activación | Criterio de aceptación | Estado técnico |
|---|---|---|---|---|
| ADR-IMP-001 | Release versionado + puntero atómico / symlink, Docker, Electron | Ya en IMP-03 | Alteración rechazada; corte preserva versión previa; rollback con hash | Prototipo PR135; falta rollback en navegador |
| ADR-IMP-007 (nueva) | Origen estable + preferencias tipadas en localStorage / origen por arranque | Ya | Preferencias sobreviven actualización y rollback; esquema inválido → valores por defecto | Propuesta |
| ADR-IMP-008 (nueva) | Firma Ed25519 con clave pinned / manifiesto SHA-256 solo | Antes de distribuir fuera del equipo de desarrollo | Firma inválida, clave ajena y rollback revocado rechazados | Propuesta; clave de prueba solo en tests |
| ADR-IMP-009 (nueva) | BFF local con token solo servidor / exponer API | Ya | Token ausente en navegador y en artefactos; rutas no permitidas → 404 | Propuesta |
| ADR-IMP-010 (nueva) | Episodio en memoria + exportación temporal borrada / persistencia | Ya | Tras exportar o cerrar no queda fichero temporal | Propuesta |
| ADR-IMP-011 (nueva) | Actualización no automática y no durante episodio / automática | Ya | Actualización bloqueada con episodio activo; confirmación explícita | Propuesta |
| ADR-IMP-002 | Gateway ASGI sobre router puro / exponer `BoundedHTTPServer` | Disparador T1–T5 | Dorados byte a byte; negativos de método, tamaño, host | Diferido |
| ADR-IMP-003 | OIDC + PKCE / token largo en navegador | Disparador T1, T2 o T4 | `iss`, `aud`, `nonce`, `state`; cookies y logout probados | Diferido |
| ADR-IMP-004 | PostgreSQL mínimo / localStorage para más datos | Disparador T1 o T2 | Restore a BD vacía; aislamiento por usuario | Diferido |
| ADR-IMP-005 | IaC dry-run / manual | Disparador remoto aprobado | `plan` sin recursos creados | Diferido |
| ADR-IMP-006 | RAG/vector diferido | Función aprobada y evaluación | Sin fuentes restringidas indexadas | Diferido |

**Qué debe demostrar Codex** (en PR135 o su sucesor, sobre su SHA):
- Firma: alteración, clave ajena y versión revocada rechazadas.
- Host, Origin, token y 409 de build distinto.
- Allowlist de rutas sin blood-gas ni T06.
- Episodio y temporales borrados tras exportar.
- Rollback y preferencias conservadas en navegador real.
- Tests y `npm run build` observados, no supuestos.

**Qué auditará IMP-09** sobre SHA exacto: ataques contra el launcher, cobertura de los controles anteriores y límites de accesibilidad y offline. **Esta revisión no audita el código nuevo.**

## 7. Objeciones, incertidumbres y recomendación

**P1:**
- **P1-1.** Rollback del Service Worker en el mismo origen no está demostrado (`RESULTADO_LOCAL.md` L35). Sin esa prueba, no se puede prometer coherencia.
- **P1-2.** Sin firma, el paquete solo detecta corrupción (ADR-IMP-001 y cotejo de Work). No puede distribuirse fuera del equipo de desarrollo.
- **P1-3.** Origen por arranque contradice la persistencia de preferencias. Ver §5.
- **P1-4.** Backend y actualización de la PWA instalada no están en PR135 (`RESULTADO_LOCAL.md` L31). IMP-03 completo requiere ambos.
- **P1-5.** Saturación sin 503 en el transporte base (`http_transport.py` L95–98). Resolver en el BFF.

**P2:**
- **P2-1.** Dependencias Python sin lock raíz ni runtime empaquetado. Hay que definir el mecanismo.
- **P2-2.** `npm run build` ejecuta generadores sin `--check` (`package.json` L7). Verificar en checkout limpio.
- **P2-3.** Export sin persistencia no verificado en el código de exportación.
- **P2-4.** Cifrado de disco y ACL de carpetas de usuario no verificados por la aplicación.

**Incertidumbre:** Python 3.12 en el equipo del usuario, tamaño del paquete y coste de firma. No medidos.

**Recomendación final:** local primero, híbrida opcional. Mantener PR135 como base, añadir BFF con token solo servidor, origen estable, firma Ed25519 y pruebas de rollback en navegador.

**¿Queda alguna decisión arquitectónica que impida continuar IMP-03 local?** **No.** La ausencia de contrato cloud no bloquea el modo local. Antes de distribuir a otros equipos hará falta una decisión humana: quién custodia la clave privada de firma. Eso no es necesario para pruebas sintéticas ni para desarrollo local.

**Decisiones humanas imprescindibles ahora para el modo local:** ninguna. Las 3 posibles quedan diferidas a antes de distribuir o de activar remoto.

ARCHITECTURE_DECISION: LOCAL_PRIMARY_HYBRID_OPTIONAL
IMP01_TECHNICAL_DECISIONS: DELIVERED
```

## Cotejo de Work/Codex

Se adopta como dirección técnica propuesta la arquitectura local con compañero Python y la separación de una futura frontera productiva. La aceptación de código, artefactos, pruebas y auditoría IMP-09 corresponde al SHA final, no a esta respuesta.

1. No borrar un episodio ni el documento que el usuario exportó como prueba de privacidad. Limpiar solo temporales propios y registrar el alcance de descargas, spool, memoria y SO.
2. Mantener preferencias y actualización instalada como requisitos: documentar su pérdida no cierra IMP-03. El cambio de origen de PR135 fue un límite reconocido, no el diseño definitivo.
3. La cabecera de versión puede llamarse X-Emergency-Revision en lugar de X-Emergency-Build; debe existir una sola convención validada y rechazo explícito de cliente obsoleto.
4. Una propuesta anti-rollback no debe impedir volver a la versión anterior firmada, confiable y compatible. No inventar que existe ya una lista de revocación.
5. No imponer Python 3.12 global: aceptar el intérprete/ABI real empaquetado o requisito exacto comprobado, con dependencias y licencias verificadas. Una carpeta de fuentes no demuestra instalación reproducible.
6. CSP no prueba egress de Python. Los proveedores/LLM y entornos heredados deben quedar cerrados por controles del proceso. Token de proxy no equivale a identidad médica ni aislamiento entre usuarios del mismo SO.
7. No excluir una función individual determinista de gasometría únicamente porque OCR/T05 sea laboratorio. Las rutas realmente necesarias se inventariarían sin modificar motores. MCP operativo de coordinación tampoco implica MCP empaquetado en el producto.
8. No convertir cifrado del disco, ACL o TCO cloud en nuevas barreras universales de instalación sintética. Conservar sus límites para datos reales, distribución o activación remota.
9. El cotejo complementario de Work confirma Run Madrid/Bélgica tier 1; la tarifa SQL europea exacta sigue pendiente. No se adopta la repetición de la incertidumbre antigua como un hallazgo nuevo de precios. No se han rehecho consultas ni aceptado contratos.
10. Preparar contratos portables no autoriza exponer el servidor loopback. Un gateway remoto requerirá frontera productiva, identidad, permisos, pruebas, tratamiento y autorización pertinentes.

La custodia de la respuesta íntegra, JSON original y recibo está en `IMPLEMENTACION_SIGUIENTE_20261127/EVIDENCIAS/CLAUDE`. La lista de auditoría allí es preparación de Work, no una ejecución de Antigravity. Las pruebas previas idénticas se reutilizan con su SHA; las nuevas funciones y riesgos se prueban aparte. No nueva aprobación de decisiones médicas ya concedidas.

CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE. Sin compra, provisión, despliegue ni modificación de ramas protegidas.
