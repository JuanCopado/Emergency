# R43 · pt-BR en el laboratorio de factores humanos

**CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.** Decisión médica vigente `MED-DEC-R39-PTBR-FINAL`, 24/11/2026.

Se verificó el SHA‑256 de los dos adjuntos idénticos `R41_ptbr.patch`: `c5e3abed03d85aabbcecb93e51cd6f79faabda11de0378316deefcf08a11708d`. El parche completo de 14 archivos aplicó con índice sobre `dcc48b3cc115a7de5f45e9a2a89d06673ba8fe15`. La rama aislada `codex/r43-ptbr-20261124` parte de `771ed2bbcc9b0457f5bb8ef75089e236fda7c1d2`, HEAD de la rama internacional tras PR99.

## Delta incorporado

El evaluador y la entrada de laboratorio usan los cuatro mensajes aprobados PTBR-MOD-01..04 y los cinco controles literales. Se activa con `?lab_locale=pt-BR` en UI `pt`. Se rechaza `?lab_locale=pt` y las variantes no admitidas en la entrada y se rechaza la exportación canónica de `pt` genérico sin variante. Se conserva el protocolo histórico para pt-PT, es y en. El paquete PTBR-PIX queda fuera del delta.

Para pt-BR, `MSG_T7_D` identifica el formato global no admitido (T7-04A, «Enviar arquivo») y `MSG_T7_B` la incompatibilidad de modalidad (T7-04B, «Selecionar modalidade» y «Enviar arquivo»). El alias `MSG_T7_UNSUPPORTED_FORMAT` conserva su tratamiento anterior. El test de React comprueba los dos resultados y el comportamiento histórico de las demás variantes.

Los 24 registros canónicos existentes, su informe Chromium, los tres PDF históricos y el manifiesto del banco conservan sus bytes. Los registros pt-BR y su informe se guardan en archivos separados. El contrato `canonical-r27-v1.2` verifica el nuevo estrato a partir de un evento observado `locale_resolved` y coteja cada sello con el manifiesto y el estímulo físico. El banco sigue `NOT_FROZEN_NOT_VALIDATED`, 10/30 con archivo y 0/30 adjudicados.

## Verificación

- Frontend · 53 archivos, 1.036 pruebas aprobadas. Typecheck y lint aprobados.
- Build con ambas banderas de laboratorio a 1 · 0/11 marcadores en 28 archivos del build de producción. El control positivo de laboratorio detectó 10/11 marcadores y el escáner devolvió 1. El marcador escrito como comentario se elimina al compilar.
- Chromium 154 · 60 ensayos técnicos en React. Avisos, foco, recuperación, encuadre y cargas válidas conformes; 32 exportaciones de prueba, 8 rechazos de `pt` genérico y 20 ensayos fuera de exportación. Se incorporan únicamente los 8 sellos nuevos de pt-BR.
- Python · [comparación de regresiones](R43_CODEX_PYTHON_REGRESIONES.md).

La PR se mantiene en borrador. Requiere seis checks C12, Clinical QA y auditoría independiente de Antigravity antes de fusionar.
