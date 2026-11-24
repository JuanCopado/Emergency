# R41 · Diagnóstico de conflictos de PR89

Fecha: 24/11/2026.

## Identidades

- PR89 HEAD: `b969e5010014e292a4b47bd38ac06509f6c376fb`.
- Receptor actual: `dcc48b3cc115a7de5f45e9a2a89d06673ba8fe15`.
- Ancestro común: `bd2a70a2564cd3f7d1b91aab11e012f900ec58d5`.
- Divergencia: PR89 **5 commits por delante y 47 por detrás**.
- GitHub: `OPEN`, `DRAFT`, `mergeable=false`.

## Causa

PR89 arrastra cambios R24 de interfaz, oracle y laboratorio que el receptor ya incorporó y evolucionó después. Hay solapamiento en `STATE.md`, interfaz, traducciones, pruebas UI, `clinical/CHANGELOG.md` y ficheros del laboratorio. Fusionar o rebasar la rama original mezclaría historia obsoleta con el banco.

## Resolución adoptada

- **PASS:** rama nueva desde el receptor actual; sin force-push y sin modificar la rama original.
- **PASS:** se trasladan únicamente el manifiesto, bytes del banco, auditoría, generador, dry-run, fixtures y pruebas focales de PR89.
- **PASS:** no se reintroducen cambios antiguos de UI, traducciones, oracle R24, `STATE.md` ni changelog.
- **PASS:** los cinco archivos físicos nuevos se añaden; los tres PDF existentes se sustituyen por sus variantes reproducibles con campos identificadores vacíos.
- **BLOCKED:** PR89 original continúa sin ser fusionable y debe considerarse sustituida por la PR limpia; no se cierra automáticamente.

## Delta seleccionado desde PR89

- Nuevos: `S1-08.jpg`, `S2-08.jpg`, `S1-09.webp`, `S2-09.jpg`, `S2-13.jpg`.
- Sustituidos por bytes reproducibles: `S1-13.pdf`, `S2-14.pdf`, `S2-15.pdf`.
- Sin cambio de bytes: `S1-14.png`, `S1-15.jpg`.
- Pendientes: 20 archivos clínicos/sintéticos autorizados; no se fabrican ni se sustituyen por QA.
