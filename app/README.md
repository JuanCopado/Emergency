# Emergency — Referencia de perfusiones para Urgencias/UCI (Sprint 1)

> **Borrador — contenido NO validado clínicamente.** Todos los datos clínicos proceden del paquete de referencia *emergency-medicine* v1.35 y están pendientes de revisión humana (UCI, cardiología, farmacia hospitalaria). Prevalecen siempre los protocolos locales y el juicio clínico.

PWA (funciona sin conexión) para médicos de urgencias y cuidados intensivos: fichas de 17 fármacos en perfusión continua del adulto (vasoactivos/inotrópicos y sedoanalgesia de UCI) y una calculadora dosis ↔ mL/h que muestra toda la aritmética.

Interfaz en **español (por defecto)**, inglés (maestro), portugués europeo y chino simplificado; tema claro/oscuro; accesible (WCAG AA, ARIA, teclado); diseño *mobile-first*.

## Requisitos y comandos

Node 22 y npm.

```bash
npm install          # dependencias
npm run dev          # servidor de desarrollo (http://localhost:5173)
npm run build        # typecheck (tsc -b) + build de producción en dist/ (incluye service worker)
npm run preview      # sirve dist/ en http://localhost:4173
npm run test         # Vitest (motor de cálculo, datos, i18n, UI)
npm run lint         # ESLint
npm run typecheck    # TypeScript estricto sin emitir
npm run icons        # regenera los PNG del manifest a partir de public/favicon.svg
npm run screenshots  # capturas Playwright de dist/ en screenshots/ (requiere build previo)
```

`icons` y `screenshots` usan `playwright-core` con un Chromium ya instalado (no descargan navegadores). Ruta autodetectada en `scripts/chromium.mjs`; se puede forzar con `CHROMIUM_PATH=/ruta/chrome`.

Para regenerar los valores de referencia de Python (validación cruzada):

```bash
python3 scripts/python_expected.py /ruta/al/paquete/v135 > src/lib/__fixtures__/python-expected.json
```

## Arquitectura

Vite + React 18 + TypeScript (strict) + Tailwind CSS + react-router + i18next + vite-plugin-pwa. Sin backend.

```
src/
  config/brand.ts          Marca (nombre, colores, versiones) — ÚNICO punto a cambiar para renombrar
  data/
    drugs.json             Base de datos clínica (inglés, maestro) — 17 fármacos + 3 módulos
    schema.ts              Esquema zod + tipos TypeScript (validación al cargar y en tests)
    index.ts               Acceso a datos (getDrug, defaultPreparation, …)
    moduleGroups.ts        Grupos de módulos del catálogo v1.35 (disponibles / próximamente)
  lib/
    infusion.ts            Motor de cálculo puro (sin UI)
    titration.ts           Valores por defecto de la tabla de titulación
    format.ts, useFormat   Formato numérico por idioma, mcg/µg, parseo con coma o punto
    storage.ts             localStorage con try/catch
  i18n/                    i18next + locales/{en,es,pt,zh}.json
  state/settings.tsx       Idioma, tema, símbolo de microgramos (persistidos)
  components/              Layout, banner de borrador, badges, campos numéricos, logo SVG
  pages/                   Home, DrugList, DrugDetail, Calculator, Settings, About, NotFound
scripts/                   generate-icons, screenshots, python_expected.py
```

### Motor de cálculo (`src/lib/infusion.ts`)

- Unidades: `mcg/kg/min`, `mcg/kg/h`, `mg/kg/h`, `mcg/min`, `mg/h`, `units/min`, `units/h`, `ng/kg/min`; concentraciones en `mcg/mL`, `mg/mL`, `ng/mL` y `units/mL`, con conversión automática de masa e incompatibilidad masa ↔ unidades detectada.
- `doseToRate` (dosis → mL/h) y `rateToDose` (mL/h → dosis), `concentrationFromAmount` (cantidad/volumen final), `convertDose`, `buildTitrationTable`, `computeBolus`.
- Sin peso en una dosis por kg devuelve `needs-weight` con la **fórmula simbólica** y ningún ritmo específico del paciente.
- Precisión completa internamente; redondeo a 0,1 mL/h solo al mostrar.
- Los **bolos/cargas** devuelven dosis, volumen y tiempo; nunca mL/h.
- Cada resultado incluye los pasos aritméticos estructurados que la interfaz muestra y traduce.

### Idiomas

El inglés es el idioma maestro del contenido clínico: los textos clínicos de `drugs.json` se muestran en inglés en todos los idiomas, con un aviso. La interfaz está completamente traducida. Los nombres de los fármacos están traducidos en `drugNames` y la búsqueda los reconoce (p. ej. «noradrenalina»). Un test garantiza que las cuatro traducciones tienen las mismas claves y variables.

### PWA

`vite-plugin-pwa` (generateSW, `autoUpdate`): precache de toda la app, `navigateFallback` para las rutas SPA, manifest con iconos 192/512/maskable, `theme-color` y meta de Apple.

## Procedencia de los datos

Fuente: paquete *emergency-medicine* v1.35 (solo lectura):

- `modules/cardiovascular.md` § `vasoactive-inotrope-infusions`: noradrenalina, vasopresina, adrenalina, dopamina, dobutamina, milrinona, levosimendán, fenilefrina, angiotensina II.
- `modules/procedures-pharmacology.md` § `icu-sedation-analgesia-infusions`: fentanilo, remifentanilo, morfina, hidromorfona, propofol, dexmedetomidina, midazolam, ketamina; § `medication-selection-safety`: reglas de seguridad.
- `references/evidence-registry.json`: estado de la evidencia (ambos módulos «yellow», revisados el 29/09/2026).
- `scripts/infusion_calculator.py`: validación cruzada de la aritmética.

Reglas de extracción: los valores se transcribieron **literalmente**; lo que no aparece en la fuente es `null` y la app lo muestra como «No indicado en la fuente». Todos los fármacos llevan `reviewStatus: "draft-pending-clinical-review"` y la referencia a su módulo. Las 34 perfusiones de ejemplo (70 kg o dosis fija) y las 3 cargas/bolos de los módulos se reproducen en los tests.

### Campos en `null` y ambigüedades de la fuente

- **Diluyente no indicado**: noradrenalina 8 mg/100 mL, adrenalina (la fuente remite a confirmar el diluyente local), dopamina (premezcla), dobutamina, fenilefrina, angiotensina II 2,5 mg/500 mL, remifentanilo, morfina, hidromorfona, dexmedetomidina.
- **Cantidad/volumen no indicados**: levosimendán 0,05 mg/mL, propofol 20 mg/mL, dexmedetomidina 8 mcg/mL (solo se da la concentración).
- **Sin dosis de inicio explícita**: adrenalina, milrinona, fentanilo, morfina, hidromorfona, midazolam, ketamina (se da rango de mantenimiento). **Sin máximo numérico**: noradrenalina («no absolute labelled maximum»), propofol (límite de 4 mg/kg/h en otra unidad, guardado como texto).
- **Posición**: remifentanilo no tiene frase de posición propia (null).
- **Levosimendán**: «12,5 mg (5 mL) in 500 mL» se interpretó como volumen final 500 mL (así da exactamente 25 mcg/mL); si se añaden 5 mL a 500 mL serían ≈24,75 mcg/mL.
- **Vasopresina**: inicio 0,01 U/min (ficha EE. UU.) frente a 0,03 U/min fijas (práctica); se guarda como 0,01–0,03 con el texto de la fuente.
- **Noradrenalina**: preparación expresada en base; 8 mg de tartrato ≈ 4 mg de base (advertencia mostrada).
- **Redondeo de la fuente**: la fuente muestra 5,25 / 12,25 mL/h (exacto) y 2,6 / 13,1 / 7,9 mL/h (ya redondeados). La app muestra siempre 0,1 mL/h (5,25 → 5,3) y el valor exacto al lado.

## Pruebas

- `src/lib/infusion.test.ts`: validación del JSON con zod; coherencia cantidad/volumen/concentración; los 34 ejemplos resueltos; comparación con `infusion_calculator.py` (tolerancia 1e-9); todas las unidades en ambos sentidos; validación de entradas; redondeo; tabla de titulación; bolos.
- `src/i18n/i18n.test.ts`: paridad de claves, plurales y variables en las 4 traducciones.
- `src/test/ui.test.tsx`: calculadora (ejemplo de noradrenalina a 70 kg, sin peso → fórmula, modo inverso, concentración personalizada, avisos de máximo, carga de milrinona), ficha, filtros, cambio y persistencia de idioma y tema.

## Hoja de ruta

**Sprint 2**
- Perfusiones pediátricas (módulos de `special-populations`), con límites por peso y edad.
- Módulo de bolos/ISR (`airway-rsi`, `sedoanalgesia`): dosis, volumen y tiempo; kits de intubación.
- Catálogo completo de módulos (106 IDs de `module-index.md`) navegable.
- Pipeline de contenido desde el paquete de la skill: parser de los `.md` → `drugs.json` versionado, diff entre versiones, validación con zod y con las pruebas de Python, actualización automática en la PWA (versión de contenido + aviso de cambios).
- Flujo de revisión clínica: estados (borrador → revisado → publicado), revisor y fecha por fármaco, comentarios y registro de auditoría; traducción clínica tras la validación.
- Concentraciones estándar locales configurables (Portugal/Azores, farmacia) que sustituyan a las de ejemplo.

## Marca

El nombre provisional es «Emergency». Para cambiarlo basta con editar `src/config/brand.ts` (nombre, colores, descripción del manifest) y, si se quiere, `public/favicon.svg` + `npm run icons`. El logotipo es un símbolo SVG original (cruz y trazo de ECG), sin logotipos de terceros.
