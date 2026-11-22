# PR70 · recibo de integración · 22/11/2026

**Integración verificada.** Este recibo documenta las correcciones de problemas actuales autorizadas por el propietario y la evidencia observada antes y después de la fusión. La auditoría profesional se entregó antes del lote de correcciones.

## Identidad de la entrega

- Repositorio: `JuanCopado/Emergency`; [PR70](https://github.com/JuanCopado/Emergency/pull/70).
- Base auditada: `0e68e5ee654e7be452cbb7cb5e5fb22b8b1127ed`.
- Head comprobado: `e6a4e00cfd89d1aa7a625f9ef3d3ed9efe0ac1a1`.
- Árbol del head: `4f3331e48474816d4487635bae2c05d24849acee`.
- Merge de prueba de GitHub: `25dc1df7bdc5aeaa2937ba50c5ed20b5f4b18404`; corresponde al head sobre la base, no al commit definitivo de integración.
- Commit integrado: `e8de202d874c6db588d3561ff13859e5ee53c96d`.
- Árbol integrado: `4f3331e48474816d4487635bae2c05d24849acee`.

## Doce puntos del lote

| ID | Corrección incluida |
|---|---|
| C01 | Frontera local de Host/Origin, credencial privada entre procesos y rechazo de exposición directa por red. |
| C02 | Rechazo explícito de textos superiores a 120.000 caracteres; conservación íntegra dentro del límite. |
| C03 | Detector de correo con recorrido lineal y comprobación de trabajo proporcional. |
| C04 | Etiquetas identificativas ES/PT/EN/ZH, conservando espacios Unicode y saltos de línea al pegar documentos. |
| C05 | Mensaje neutro sobre ausencia de identificadores detectados, límites visibles y revisión humana conservada. |
| C06 | Borrador por episodio en memoria, regreso desde gasometría y aislamiento de respuestas antiguas. |
| C07 | Inicio y recuentos de guías derivados del catálogo vigente. |
| C08 | Controles operativos de escalas/importación localizados, con contenido clínico canónico preservado. |
| C09 | Identidad Git de aplicación separada de la versión del catálogo adulto. |
| C10 | Conciliación de documentación sobre funciones, aceptaciones y alcance de QA; selector existente, arranque por plataforma y motor local de perfusiones precisados. |
| C11 | Nombre de PROC-SP-003 concordante con conservación del segmento, sin cambiar su técnica. |
| C13 | Aceptación MCDT vinculada a la revisión enviada; respuestas obsoletas descartadas. |

C13 ya existía en la base y se incorporó al detectarlo durante la revisión cruzada. El checklist cierra C01–C11 y C13 como OK tras comprobar el merge. C10 incluye la conciliación de las instrucciones vigentes y los comandos de arranque por plataforma.

**C12 permanece PENDIENTE DE ACCESO:** la protección automática de ramas y exigencia de checks no se han activado. La propuesta administrativa está preparada, pero requiere una conexión con permisos de escritura y lectura posterior de la configuración efectiva.

## Verificación del candidato

| Ejecución | Resultado confirmado |
|---|---|
| [Clinical QA push 44994486269](https://github.com/JuanCopado/Emergency/actions/runs/44994486269) | PASS: 1.205 pruebas contabilizadas, 14 omitidas, 1.191 ejecutadas sin fallos; 150,532 s. |
| [Clinical QA PR 44994489023](https://github.com/JuanCopado/Emergency/actions/runs/44994489023) | PASS: mismo conteo; 179,670 s. |
| [App UI QA 44994489047](https://github.com/JuanCopado/Emergency/actions/runs/44994489047) | PASS: 947 pruebas en 47 archivos; recorridos de navegador confirmados. |

Clinical QA aprueba catálogo normalizado, grafo de procedencia, integridad de módulos, cobertura de evidencia, procedencia de casos e imágenes, registro de fuentes y plantilla ciega. Permanecen los avisos históricos; estos resultados técnicos no renuevan fechas de revisión científica.

El primer ciclo, sobre `bdb0dfc2`, falló en 67 subcasos de cinco métodos de `test_patient_weight_http.py`: su helper omitía Origin y credencial, y recibía 403 antes de comprobar los resultados esperados. Se corrigió exclusivamente ese cliente mediante `request_metadata(server)`, conservando entradas, expectativas 200/422 y aserciones numéricas y de exportación. Sus seis métodos pasaron localmente y el nuevo ciclo remoto terminó en PASS. El fallo inicial permanece documentado.

### Seguridad

[Security and quality PR](https://github.com/JuanCopado/Emergency/actions/runs/44994489082) y [push](https://github.com/JuanCopado/Emergency/actions/runs/44994486219): seis jobs PASS en cada ejecución (Trivy, Semgrep, cobertura real, T05 Windows, T06 Linux y Sonar). Sonar del PR registra 88,7 % de cobertura nueva y 0,0 % de duplicación; el análisis de rama, con otro ámbito de comparación, registra 84,1 % y 0,2 %. Ambos gates aprobaron.

El ciclo intermedio c5d329bc había fallado por 77,0 % de cobertura nueva y seguridad B. El delta enumera los orígenes locales, comprueba el plugin importado mediante HTTP real y refuerza la identidad Git con ejecutable absoluto y entorno acotado. Los umbrales y las exclusiones no cambian. La única anotación restante del PR es S1313 sobre `::ffff:127.0.0.1`, revisada en el [expediente HTTP](../../clinical/qa/HTTP_LOCAL_BOUNDARY_SONAR_20261122.md); no se ocultó ni se aceptó administrativamente. El resumen informa una incidencia nueva, cero aceptadas y cero Security Hotspots.

Persiste el error interno de deserialización Protobuf/UTF-8 observado en la auditoría; los logs continúan y terminan con gate PASS. No determinan el dato concreto ni el alcance del fallo, por lo que no se describe el análisis como libre de incidencias.

### Comprobación posterior a la integración

La API de GitHub confirma PR70 cerrada y fusionada, y la rama `codex/v144-international-scope-20261116` apunta a `e8de202d874c6db588d3561ff13859e5ee53c96d`. El árbol integrado `4f3331e48474816d4487635bae2c05d24849acee` coincide byte a byte con el del head comprobado. La tabla anterior acredita la CI previa a integrar; no se atribuye a una ejecución posterior. Los workflows automáticos posteriores se identifican por el SHA del merge. Este recibo y el cierre del checklist se publican como un seguimiento documental separado. `main` permanece en `4f37263f581c41874fd3253147e6679b0b0685d8`; RC1 y v1.43 no son destinos de esta entrega.

## Alcance preservado

Calculadoras, fórmulas, dosis, referencias, registro de evidencia y aceptaciones clínicas conservan su contenido. En módulos solo cambian títulos de dos índices de procedimientos; el cuerpo de PROC-SP-003 permanece intacto. Se mantienen 46 IDs y el alcance aceptado de los 19 contratos antes bloqueados.

El registro conserva 131 módulos, 129 GREEN y 2 YELLOW; el estado global sigue siendo **CLINICALLY_PENDING**. Este recibo no cierra M10/R7/R8, evaluación clínica, G05, ampliaciones de plataforma, validación estructurada de procedimientos, Narrador o restauración operativa, ni acredita una instalación asistencial.
