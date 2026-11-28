# Integración total individual · v0.7

Estado de preparación: candidato único aislado, instalado y con aceptación nativa medida. PR137 en borrador; no es una liberación clínica. La CI del HEAD final requiere su recibo independiente.

## Identidad y dependencias

Receptor conservado: `fa2381dcfe77253f575ac843860b3167125f1e1e`.
Composición ejecutable: `b54301e891110715ed9a388723155f8c354b07b6`.
Árbol: `e26de7d86d9bf4277260ff4a75ab939f8e1958bd`.
PR única de candidato: https://github.com/JuanCopado/Emergency/pull/137
Rama única: `integration/individual-total-20261128`.

| Fuente | HEAD incorporado como ancestro |
|---|---|
| PR129 | a3ae85412a868c105c64ca8b491e1cb3a1df065c |
| PR130 | f32d211eed6a7baa7c42aadae583f6726e9e7e9b |
| PR131 | 3cc5139b149feef390e6ceaa7358e2425d92620a |
| PR132 | 780cf736b29d9e176a850530797115c32638aab0 |
| PR133 | e4d3f71975a75389bbc9df146670b5823ce4677b |
| PR134 | 06ef1e030e70915e257d19576f25ae8dbd37f19e |
| PR135 | 8699cdc4f34bff378ae5ef69498bcfd1d944e3bd |
| PR136 | 27d46f8e452418963e62af17b402a098429e7bcb |

PR129→130→131→132→133 ya forman una cadena; se incorporó su último HEAD una sola vez. PR136 conserva PR135 y el incremento firmado. Se añadió PR134 vigente mediante merge independiente, sin conflictos. No se reescriben las ramas fuente ni se retargetean formando ciclos. La PR del candidato apunta al receptor internacional vigente para medir la composición completa; las PR fuente permanecen abiertas, sin fusionar ni atribuirles integración en el receptor protegido.

Los cambios ejecutables respecto a PR136 se limitan al frontend Home, localizaciones y sus pruebas, hooks de admisión de activos y laboratorios RAG/interoperabilidad/MCP procedentes de la pila. Los once módulos de instalación/supervisión y el cierre de scripts clínicos mantienen sus bytes. No se cambian dosis, fórmulas, aprobaciones, fuentes canónicas ni fechas de revisión.

## Funcionalidades y destino

| Funcionalidad | Clasificación | Alcance efectivo |
|---|---|---|
| Módulos clínicos y referencias propias | Preparadas para evaluación final | Consulta existente y fuentes versionadas; no implica disponer de todos los originales editoriales. |
| Farmacología, perfusiones y calculadoras | Preparadas para evaluación final | Frontend existente y motores locales; conservan controles y alcance de cada caso/producto. |
| Nota clínica | Preparada para evaluación final | Backend local, episodios y revisión de privacidad/terapia existentes. Preparar un adjunto transitorio no admite imágenes al banco. |
| Exportación PDF, Word y JSON | Preparada para evaluación final | Exportador canónico; bloquea hasta satisfacer los controles aplicables. Fixtures de QA no son aprobaciones médicas. |
| Clinical Minimal | Preparada para evaluación final | Opt-in `/?design=clinical-minimal`; búsqueda accesible, teclado y composición IME. La IME DOM sintética no certifica una IME del SO. |
| PWA, actualización y rollback | Preparadas para evaluación final | Mismo origen, confirmación por pestaña, preservación de notas/preferencias y API ligada al SHA. Aceptación conjunta del nuevo paquete requiere recibo propio. |
| RAG y generación | Experimental / activación clínica deshabilitada | Herramientas locales de laboratorio, corpus permitido y preguntas predeclaradas; sin LLM real, consultas de pacientes, endpoint clínico ni activación asistencial nueva. |
| Emergency MCP | Experimental opcional | Stdio de solo lectura con SDK dedicado existente; snapshot fijado `3cc5139`, no servicio vivo de GitHub/Drive. No se añaden sus dependencias al backend clínico. |
| Interoperabilidad FHIR/HL7/DICOM | Experimental / conexión operativa deshabilitada | CLI y escenarios sintéticos; no servicio hospitalario ni requisito general de instalación individual. |
| POCUS e imágenes | Referencias y preparación experimental | Cero admisiones de medios al producto; banco comunicado 10/30 técnico, 20 ausentes, 0 adjudicaciones. No se incorporan originales ni derivados sin admisión. |
| OCR/T05/T06 e inferencia remota | Deshabilitadas en este paquete | Indisponibilidad explícita; existencia en el repositorio o éxito de CI nativa no implica empaquetado. |
| Identidad remota, PostgreSQL, infraestructura y almacenamiento | Ampliaciones futuras condicionales | Solo ante utilidad y autorización concretas; sin servicios remotos obligatorios, compras ni despliegue. |

Los laboratorios se conservan en un único candidato fuente para reproducción, separados del artefacto clínico instalable. No se distribuyen índices generados, extractos restringidos, respuestas completas MCP ni originales de imagen. El paquete clínico contiene únicamente sus fuentes, datos permitidos, frontend y seis wheels oficiales.

## Artefacto e instalación observada

Paquete C: `EMERGENCY_INDIVIDUAL_C_b54301e.zip`, 28.708.238 bytes, 138 archivos.
SHA-256: `17fc738b2ce36565af8ab6f1ed1fd10fb79db3d960a95f2daaaff53a6512a11b`.
Versión: `b54301e891110715ed9a388723155f8c354b07b6-0b49ed41ad5c4682`.
Contador firmado 8. Mismo editor Ed25519, huella independiente:
`02a782bd1e8f8ad24548e7535ef7e745188d0c61351c84f2eff710e6c59a56c4`.

Instalación física B5/C recibida en raíz nueva del laboratorio: B5 25,859 s y C 4,172 s compartiendo el runtime ya verificado. Python 3.12 x64 compatible previamente instalado; no se redistribuye el intérprete ni se instala nada global. La clave privada DPAPI queda fuera de Git/Drive.

Recibos de BUILD_C e INSTALL_INTEGRATED conservados fuera del repositorio. Aceptación nueva **PASS**: B5→C→B5 en la PWA nativa, mismo origen127.0.0.1:49157, consentimiento, preferencias y nota conservadas, API409, rutas nuevas bloqueadas y rollback. Tras cortar servidor y conexión, calculadora en caché5.3 y API fallida en forma explícita. Recibo TOTAL_NATIVE_CANONICAL_FINAL.json, tres pasos PASS y errors[]. Se usó el arnés canónico sin los extras de UI; no se hereda A5/B5. Los ensayos adicionales conservan sus FAIL de método separados (redimensionado, detach de sesiónCDP y Event genérico de IME); sus diagnósticos no se reetiquetan como PASS completos. Home1280/360 sin overflow, teclado y DOMIME válido fueron observados en focals separados; no se certifica IME del sistema.

## Revisión y límites

Claude Code ejecutó consulta real de solo lectura sobre b54301e, 228 s, exit 0. Su resultado original es **FINDINGS**, conservado íntegro: no se convierte en CLEAN. El cotejo independiente no confirmó el bypass de firma ni la equiparación entre adjunto transitorio y admisión de imagen propuestos. Claude no ejecutó pruebas ni revisó exhaustivamente MCP/interoperabilidad/DICOM; los resultados funcionales pertenecen a sus ejecutores.

[Auditoría de seguridad de composición](https://drive.google.com/file/d/1rmyRFiq83EMDG0vVWTc5FpzxRDWEUuq4/view) y [privacidad/PWA](https://drive.google.com/file/d/1pRasJOJSyC85K4dNXN3Ooo1avCrKpB1C/view): favorables exclusivamente a composición estática b543, sin bloqueos nuevos identificados. La auditoría previa de Antigravity PR133 no se transfiere al candidato. El nuevo envío a Antigravity y Gemini quedó impedido por activación de sus ventanas; no hay acuse ni dictamen nuevo atribuido. Se reutiliza el contraste científico anterior sin repetir decisiones médicas.

RAG focal sobre el grafo canónico: 397 nodos/417 relaciones, ocho preguntas, tres recuperaciones y cinco abstenciones, sin activación/generación. MCP real: inicialización, ocho herramientas y tres llamadas correctas en modo metadatos, sin respuestas completas persistidas. Se preserva el fallo inicial del arnés RAG por saltos de línea y su corrección al comportamiento original del constructor, sin cambiar el pin.

Las CI de las fuentes son históricas. CI, Sonar y checks del HEAD final del candidato se recogen separadamente después de publicar; no se anticipa PASS. `tools/local-installation` y `tools/emergency-mcp` están fuera de `sonar.sources`; la cobertura/gate no certifica esos componentes. No se declara WCAG completa, Lighthouse, escalabilidad ni uso asistencial sin medición.

### Recuperación tras corte durante escritura

El escritor usa exclusión y falla cerrado si existe `writer.lock`; una terminación abrupta puede dejar ese archivo. No se borra por antigüedad o PID supuesto. Una instalación activa ya verificada no se modifica para evitar ese bloqueo.

Para recuperar sin manipular un lock potencialmente activo: conservar la raíz original, cerrar el servidor propio, obtener los paquetes y claves públicas de confianza, y recibirlos en una raíz nueva mediante INSTALL_INDIVIDUAL. Verificar firmas e inventario antes de activar. No copiar `active.json`, runtimes incompletos ni recibos a mano. La raíz nueva tiene otro origen y las preferencias del navegador no migran automáticamente: conservarlas/exportarlas desde el origen original si está disponible. No se promete recuperación de episodios no guardados ni borrado seguro. La eliminación de un lock exige una revisión operativa explícita de exclusividad; no se automatiza en esta integración.

Este límite operativo permanece documentado; no equivale a un bypass criptográfico. No se refactorizan las dos fronteras distintas de supervisión Job por parecido de código.

**CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.**

