# CORT-20261126 v2 — Corticoides adultos/pediatría, pautas cortas y comparador

Base: `228cd21d75d14e1012beb7f5dfe82c2c920c4ccc`. Rama: `codex/corticosteroids-therapeutic-review-20261126`. Implementación autorizada por el propietario en el despacho del 26/11/2026. **CLINICALLY_PENDING**; sin aprobación global ni despliegue nuevos.

## Resultado

Se añade una consulta de corticoides bajo el ámbito existente `medication-selection-safety`, sin nuevos IDs de módulo ni cambios en las 45 fórmulas registradas. El catálogo canónico versionado se proyecta al cliente mediante un generador con huella de fuente y `--check`. La página `/corticosteroids` utiliza controles propios ES/PT/EN/ZH; las fichas clínicas siguen en español y lo declaran.

El comparador exige fuente, vía sistémica oral/IV y tipo de cantidad (una dosis o total de 24 horas), y calcula en mg con la tabla íntegra elegida. Rechaza texto/unidades mezcladas, separadores ambiguos, valores no finitos, cantidades no positivas, desbordamiento y pérdida positiva a cero. Cualquier edición elimina el resultado anterior. No decide tratamiento, intervalo, equivalencia mineralocorticoide, retirada o dosis pediátrica.

## Cambios clínicos delimitados

- Se conserva la pauta adulta de crisis suprarrenal y la tabla RCH de crisis pediátrica ya aceptadas. No se transfieren los 200 mg/día del adulto al niño, ni se añade cálculo por edad/peso.
- Se completa el hueco de `sepsis-shock`: SSC 2026, recomendación condicional de corticoides IV, certeza baja; régimen frecuente adulto atribuido a SCCM 2024, sin automatizar duración ni preparación.
- Se hace explícito en `anaphylaxis` que los corticoides no son rutinarios y no sustituyen o retrasan adrenalina/reanimación. Los contratos de adrenalina y sus aceptaciones permanecen.
- La consulta pediátrica recoge SSC 2026: no hidrocortisona si líquidos/vasoactivos restauran estabilidad; evidencia insuficiente en shock persistente; sí cobertura de estrés ante insuficiencia suprarrenal sospechada/documentada.
- Se enlazan otros usos ya existentes en sus módulos; no se duplican algoritmos de asma, EPOC, crup, infección SNC o urgencias tiroideas.
- Se añade `### bell-palsy` dentro de `ent-emergencies`, con actuaciones iniciales, medicación, monitorización, reevaluación y destino; la protección corneal y los diagnósticos alternativos quedan explícitos. La pauta de referencia es la única estudiada por Sullivan aquí seleccionada: prednisolona 25 mg cada 12 horas durante 10 días.
- La ficha distingue la recomendación AAO-HNSF desde 16 años del borrador adulto de la aplicación desde 18 años. Los menores de 18 años, incluidos 16–17, conservan consulta y revisión individual sin una pauta adulta prellenada. BellPIC no se presenta como prueba definitiva de ausencia de beneficio: fue insuficiente para excluir un beneficio o daño importante.
- El componente de pautas cortas enlaza asma adulta, EPOC, asma pediátrica y crup a sus motores existentes. Añade la recomendación ESE/Endocrine Society R2.1 sobre retirada de cursos verdaderamente cortos, con revisión del tratamiento previo y sin suspender por defecto terapia crónica o sustitución suprarrenal.
- La revisión de cierre detectó y completó la banda de corticoide sistémico de asma de **12–17 años**, distinta de la de 6–11. Se comprobó la formulación explícita para adolescentes en GINA 2026, Box 9-2: prednisona/prednisolona 40–50 mg/día durante 5–7 días. Se conserva el párrafo y sus límites íntegros en la referencia pediátrica; las bandas son alternativas para selección médica y no una dosificación automática por edad.

## Discrepancias y fuentes

Endotext 2018 y ESE/Endocrine Society 2024 mantienen valores diferentes para dexametasona/betametasona y semividas. Se preservan ambos presets y versiones. La actividad mineralocorticoide se atribuye solo a Endotext y queda fuera del cálculo.

RCH, actualizado en octubre de 2024, tiene tablas de crisis y cirugía con una diferencia de banda a los seis años. Se usa exclusivamente la tabla de crisis existente. Se conserva el plan individual del niño y no se asigna automáticamente una banda.

El JSON asociado identifica las 15 referencias, URLs, versiones, localizadores y límites de acceso. Society for Endocrinology se recuperó mediante indexación oficial; la apertura directa devolvió HTTP 403. Endotext, RCH y recomendaciones SCCM se leyeron en sus páginas; el PDF ESE y las secciones RCUK se recuperaron. En la ampliación Bell, la dosis de Sullivan se comprobó en los métodos indexados del editor; la apertura directa devolvió HTTP 403. BellPIC se verificó en el resumen primario, con PDF del editor bloqueado; no se declara lectura íntegra de esos dos ensayos. La recomendación ESE de cursos cortos se abrió en la página oficial. No se interpreta indexación o QA técnica como una revisión clínica global.

El mismo expediente registra aparte la fuente del módulo de asma: GINA 2026, Box 9-2, cuya recomendación explícita para adolescentes se recuperó del informe oficial. Esta adición no altera las 15 fuentes del catálogo del comparador ni promueve las fechas de revisión de otros módulos.

## Verificación focal observada

- Python: **7/7** comprobaciones de catálogo, fidelidad, fuentes y separación de pautas, incluidas la dosis de Bell y la frontera pediátrica.
- Frontend: **35/35** pruebas del comparador y de interfaz, incluidos cuatro idiomas y la nueva ficha de pautas cortas.
- ESLint de los archivos del bloque corticoides: **PASS**.
- Generador `--check`: **PASS**.
- `git diff --check`: **PASS**.
- Registro de fórmulas y registro de evidencia: sin modificaciones en la comprobación focal.

No se atribuyen aquí build/typecheck global, navegación real o resultados ejecutados por otros colaboradores. La integración de ruta, navegación, comprobación de build y documentación común corresponde al coordinador. La validación prospectiva y los estados globales conservan su alcance anterior.

La tentativa anterior de QA visual quedó bloqueada por el entorno: el lanzador Chromium carece de su binario y la descarga oficial Playwright devolvió HTTP 403. No produjo capturas ni resultados visuales válidos. La ampliación v2 no repite descargas ni presenta una prueba de navegador como superada.
