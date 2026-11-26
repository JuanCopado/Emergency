# Supercoordinación final · candidato técnico y conciliación

26/11/2026. Repositorio JuanCopado/Emergency. Base internacional verificada `228cd21d75d14e1012beb7f5dfe82c2c920c4ccc`. Rama propuesta `review/final-closure-20261126`. La rama internacional está protegida por C12 y la orden actual prohíbe modificar ramas protegidas: se prepara un candidato aislado, sin fusionar PR111–114 ni cambiar el receptor, main, RC1 o producción.

`FUENTES_CANDIDATO.json` identifica los cuatro HEAD exactos y sus deltas: 37 archivos, cero archivos solapados, más dos documentos centrales. La composición mediante parches conserva los commits fuente en sus ramas; no es una fusión consumada ni una auditoría favorable implícita. Se incluye el delta UI acotado de PR111, no los prototipos UX/UI 2.0 pendientes de selección estética.

## 1. Estado clínico vigente

El registro canónico conserva **129 GREEN, 2 YELLOW y 0 RED**, 131 módulos. Los dos YELLOW son `clinical-image-interpretation` y `clinical-note-diagnostic-support`. El registro y sus estados no se modifican. GREEN en ese registro no sustituye la aprobación de un nuevo candidato, una validación prospectiva o la conciliación operativa aplicable. Estado global CLINICALLY_PENDING; NO_GO_CLINICAL_RELEASE.

## 2. Frente A · R89/R99 y POCUS

**COMPLETADO:** custodia física previamente verificada de 13 textos primarios R89 (12 PDF y un manuscrito HTML), tres correcciones y cuatro originales POCUS. Se reutilizan recibos, hashes, páginas y medidas de las ejecuciones identificadas en PR112 y sus fuentes; no se renueva last_checked. La corrección documental de PR112 revierte 100 secuencias de mojibake mediante inversión UTF-8/Windows-1252 comprobada. Identificadores, URL, tamaños, páginas, dimensiones y hashes técnicos permanecen iguales; ningún original se altera.

**PARCIAL/BLOQUEADO:** el PDF editorial AHA2024 sigue devolviendo403. El HTML PMC es un manuscrito, no se presenta como versión editorial. La tablaI de IFEM p41 conserva25 marcas no legibles. Una copia pública alternativa EMSSA de63p, 2.100.337bytes, SHA256 `7518dfc5d8745d78fc7b53c636c55acbd95db641cfdfc1946e891ad7bacfad9d`, recuperada por Codex y renderizada por PDFium y Poppler, tampoco permite leer esas marcas; queda auxiliar, sin sustituir el original PDF.net. Las fuentes prestadas y AAD conservan restricciones de redistribución/carga en IA. La adquisición no constituye lectura científica íntegra o revisión médica.

Los expedientes científicos adicionales trabajan con18 entradas; material asociado a18 entradas no equivale a18 documentos íntegros o18 revisiones completas. Se conservan las revisiones documentales por IA ya acreditadas en su alcance y cero revisiones clínicas humanas registradas. La matriz científica y los permisos de cada fuente son la autoridad para los pendientes particulares.

R99: cuatro originales están recibidos y verificados, no cuatro estímulos clínicamente aceptados. El nuevo candidato S2-12 Gels2023 figura4B tiene procedencia y licencia CC BY4.0 documentadas, pero permanece pendiente de condición experimental sin derrame/equivalencia, captura móvil y revisión humana. El contrato acepta ventana subxifoidea/pulmonar; no se impone una ventana estandarizada adicional. El panel2E anterior conserva CHANGES_REQUIRED.

## 3. Frente B · banco experimental

**COMPLETADO:** 30 posiciones canónicas identificadas; distribución M1=8, M2=4, M3=18. Diez archivos canónicos con identidad técnica y veinte posiciones sin archivo incorporado; cero adjudicaciones individuales. Los controles M2 se valoran según su defecto intencionado y QA-01/02 quedan fuera de las30 posiciones. PR113 conserva intactos manifiesto y blobs históricos, recibe el original S1-01 de Commons como candidato y añade `*.pdf -text` para evitar alteraciones CRLF en Windows. No se cuenta la copia de mayor resolución como un caso nuevo.

**PARCIAL:** se recuperó otro expediente vigente con diez tomas físicas distintas y un paquete ya preparado de las cinco tomas seleccionadas por el propietario: S1-10, S2-10, S1-11, S2-11 y S1-12. Se reutiliza `R86_FOTOS_PRUEBA_20261126/CIERRE_SELECCION_Y_ENTREGA/ENTREGA_CANDIDATOS`, sin crear otro lote. La adenda final S1-12 prevalece sobre un resumen que todavía decía cuatro selecciones. Estas aceptaciones son para preparación con observaciones, no adjudicación clínica.

El paquete conserva cuatro JPEG con sus bytes y orientación EXIF6; S1-11 WebP es sin pérdida respecto de píxeles RGB orientados, con original conservado. S2-11 mantiene CHANGES_REQUIRED_MOIRE; S1-12, detalle limitado, altas luces y observación marginal. Las fotografías existen: las afirmaciones anteriores de ausencia total se conservan como cortes históricos y quedan superadas por los recibos actuales. Falta conformidad experimental y revisión, no adquirir nuevamente las cinco tomas ya recibidas.

Se conservan también dos candidatos SCIN del par01, con eMST documentado por la fuente y morfología/luz/equivalencia pendientes. No reemplazan el S1-01 histórico ni completan por sí solos las14 heridas abiertas. Las ocho posiciones M1 exigen su origen sintético documentado y controles específicos; no se asigna MST por apariencia o prompt. Todos los candidatos siguen fuera del manifiesto hasta cumplir el protocolo y la adjudicación del propietario. Banco NOT_FROZEN_NOT_VALIDATED.

## 4. Frente C · R5-1/R5-2/G05

**COMPLETADO en el delta técnico comprobado:** errores de lectura JSON tras HTTP200 dejan de resolverse como éxito en el cliente de nota; tres regresiones reproducen el fallo anterior. El arnés histórico usa selectores españoles coherentes y comprueba16 casos API/pantalla/JSON, PDF y Word. Se integra ese recorrido en App UI QA con artefacto y procedencia. Las ejecuciones anteriores se atribuyen a sus SHA, no automáticamente al candidato combinado.

**CORRECCIÓN PUBLICADA/PENDIENTE DE SCANNER:** dos literales surrogate aislados de una prueba se construyen ahora con String.fromCharCode. Reproducción con mapeador/esquema del tag SonarJS14.6.0.46571: dos strings AST no válidos pasan a cero, conservando los14 controles idénticos. Suite focal138 PASS y lint PASS. Fuentes y límites en `../r5-g05-20261126/SONAR_UNICODE.md`. La CI exacta debe confirmar si desaparece el diagnóstico; no se certifica exhaustividad AST por un contador o gate verde.

La CI inicial del parche y de la composición falló realmente en T06: el sello histórico incluía el test modificado. La conciliación vigente mantiene `SOURCE_PROVENANCE.json` byte-idéntico y los19 hashes originales. `CURRENT_ADAPTATIONS.json` y un original congelado permiten comprobar18 destinos idénticos y una transformación exacta del destino19, sin retirar los14 controles. Tres pruebas puras adicionales detectan retirada de aserción, cambio del original y reetiquetado de hash. Se conserva el fallo inicial y se exige repetición nativa Linux; esos tres PASS locales no acreditan transporte T06. No se presenta el estado actual como19 destinos byte-idénticos.

**BLOQUEADO para cierre global:** R5-1 requiere banco admisible/adjudicado, institución/consentimiento, estudio y datos; R5-2, corpus textual ciego independiente de cuatro lenguas por siete clases, custodio, criterios preespecificados y adjudicadores. El banco de imágenes no lo sustituye. `../r5-g05-20261126/G05_REQUISITOS.json` conserva los seis requisitos: consumidor, derechos, privacidad, RAG, QA/aceptación y PTBR-PIX. Laboratorio local verificado no habilita consumidores públicos, RAG o píxeles. PTBR-MOD no sustituye aprobación PTBR-PIX.

Las aceptaciones médicas anteriores se preservan. El parche no introduce una cuestión clínica material nueva ni exige repetir una respuesta SÍ. La decisión clínica final corresponde al propietario; Farmacia es consultiva.

## 5. Frente D · seguridad, integración y agentes

Los recibos de PR111–114 conservan su CI real. El HEAD anterior PR114 `01f235c` tuvo tres workflows y nueve checks success, C12 seis/seis, pruebas nativas T05 Windows y T06 Linux, Semgrep/Trivy sin hallazgos bajo sus políticas y Sonar gatePASSED con diagnóstico Protobuf pendiente. Esos resultados no se atribuyen al parche posterior o a esta composición. C12 permanece activo, estricto, sin bypass; no se cambia configuración, reglas ni exclusiones para pasar controles.

**Antigravity:** nueva sesión real `b7036faf-23b4-4b82-abfd-56970605f8a5`, modelo gemini-3.8-flash-medium. Su primer acceso de enumeración fue rechazado por permisos; cero lecturas, cero imágenes y ningún dictamen válido. Exit0/SUCCESS no equivale a auditoría. No se reintentó por otra herramienta ni se cambió modo. Auditoría externa del nuevo candidato BLOQUEADA. Las revisiones previas de PR110 y PR111 conservan únicamente su alcance y SHA.

**Gemini:** CLI invocado realmente y fallido con exit41 por autenticación. Se recuperó su respuesta previa de S2-12 desde la sesión web. El nuevo encargo no pudo enviarse por bloqueo de activación de ventana, incluso tras el desbloqueo comunicado por el propietario. Investigación primaria nueva de Codex, original auxiliar IFEM y recibos se registran separados, sin atribución ficticia a Gemini.

**Codex:** ejecución técnica y revisión independiente acotada del parche Unicode, con script reproducible, fuentes/hashes y controles equivalentes. La revisión es favorable para ejecutar CI, no una firma clínica ni MERGE_READY de Antigravity. Cada escritor conserva su rama o carpeta; solo el coordinador escribe este documento central.

Graphify: la carpeta existente solo ofrece caché de detección, sin grafo final vigente reutilizable. Se usa el grafo determinista de procedencia del proyecto y las intersecciones Git para dependencias. Ponytail no está expuesto como comando o herramienta operativa en esta sesión; no se instala para esta conciliación. No se fuerza un pipeline auxiliar que duplique verificaciones.

## 6. Condiciones de GO_RELEASE y dictamen

1. Candidato exacto con QA/CI/Sonar completos y C12 satisfecho, además de compatibilidad real con receptor permitido.
2. Auditoría independiente favorable del mismo candidato y resolución de hallazgos críticos; ausencia de un diagnóstico no demuestra por sí sola validez clínica.
3. Aceptación clínica aplicable del propietario y resolución de los YELLOW/contratos/estudios que afecten al alcance de liberación; sin inferir aceptaciones por QA.
4. Banco, corpus ciego y validación prospectiva conforme a sus criterios; derechos y privacidad por fuente/campo/uso, y conciliación de producto/equipos/protocolos donde se afirme uso operativo local.
5. Alcance público, RAG o píxeles solo si se propone y autoriza ese consumo. Ninguno se habilita aquí.

**Estado de entrega:** candidato técnico propuesto, PARCIAL hasta CI del SHA final y BLOQUEADO para integración por auditoría externa no realizada y prohibición de tocar el receptor protegido. Las PR fuente permanecen abiertas. El recibo final externo publica SHA, árbol, resultados reales y comprobantes. No despliegue, liberación asistencial ni promoción automática. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.
