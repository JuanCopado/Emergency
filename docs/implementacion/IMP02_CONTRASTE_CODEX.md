# IMP-02 · Contraste primario de Work/Codex

27/11/2026. Base documental `1703435de7002172d14ed32b94df1dc6b07f4314`; alcance individual internacional. Este documento es investigación de Codex, **no una respuesta de Gemini**, ni asesoramiento jurídico o clasificación definitiva del producto. La respuesta externa se conserva por separado en `GEMINI_REGULACION.md` cuando exista. No cambia finalidades clínicas, aceptaciones, estados ni autorizaciones.

## Conclusión utilizable para implementación

Se puede preparar y probar infraestructura local con datos sintéticos, sin contratar, publicar o tratar datos reales. Debe mantenerse separada de la decisión de puesta en servicio de cada capacidad. Uso individual, ausencia de hospital y ejecución local no constituyen por sí solos exención de normativa de producto ni de protección de datos. La selección del país inicial sigue abierta; no se deduce del idioma.

MDCG 2019-11 rev.1 (junio de 2025), §§2–3 y 7, distingue recuperación bibliográfica simple de tratamiento de información con finalidad médica. Importan finalidad declarada, funciones y dependencias, no si se ejecuta en móvil, dispositivo o nube. La mera edición de texto puede diferir de interpretar datos o producir propuestas diagnósticas/terapéuticas. Delimitar módulos permite evaluar alcances concretos; no permite ocultar dependencias médicas. **No se declara Emergency exento ni clase I.** [MDCG, PDF oficial, pp.4–9 y §7](https://health.ec.europa.eu/document/download/b45335c5-1679-4c71-a91c-fc7a4d37f12b_en?filename=mdcg_2019_11_en.pdf).

Para software ya cualificado como producto sanitario, la regla 11 distingue información para decisiones diagnósticas/terapéuticas (IIa, con aumento IIb/III según impacto), monitorización y resto de software. Esto exige análisis de finalidad y daño por capacidad, no clasificación automática de toda la aplicación. La guía MDCG 2021-24 rev.1, p.46, ilustra estos criterios. Se observó un borrador de negociación de 2026 con cambios propuestos: **no se aplica como derecho adoptado**. [Guía de clasificación oficial](https://health.ec.europa.eu/document/download/cbb19821-a517-4e13-bf87-fdc6ddd1782e_en?filename=mdcg_2021-24_en.pdf).

## Matriz de capacidad y puerta de activación

Las acciones técnicas siguientes son propuestas verificables de diseño, no afirmaciones de cumplimiento ni pruebas ya ejecutadas.

| Capacidad | Datos/flujo permitido en esta fase | Acción mínima de infraestructura | Puerta antes de uso real |
|---|---|---|---|
| Biblioteca y búsqueda local | Contenido autorizado y versionado; consultas sintéticas | Integridad de artefacto; fuentes/licencias; caché solo de contenido público/autorizado; aviso de obsolescencia sin red | Finalidad y alcance de biblioteca contrastados; derechos de distribución comprobados |
| Calculadoras deterministas | Fixtures sintéticos y motores existentes | Preservar fórmulas y contratos; resultados con unidad/contexto; instalación y rollback por manifiesto | Finalidad/regla de clasificación y evidencia de cada capacidad; no suplir validación clínica con QA |
| Nota editable y PDF/DOCX | Sintéticos; ningún envío remoto de caso por defecto | Memoria efímera; exportación explícita; no cuerpos en logs; no caché autenticada; no almacenamiento web persistente de casos | Determinar qué es edición y qué es soporte clínico, responsable, base jurídica, seguridad del dispositivo/exportaciones |
| Cuentas y preferencias | `issuer+subject`, preferencias estructuradas y mínimas | OIDC, sesiones servidor, aislamiento por usuario, revocación, borrado; no campos libres de caso | Aviso de privacidad, finalidad/retención, relación contractual y proveedores/DPA correspondientes |
| API remota de referencia | Contratos sintéticos; sin datos identificables de pacientes | Gateway separado del loopback; autenticación/autorización; límites y egress; denegar claves/campos ajenos; no logs de cuerpo | Identidad, acceso cruzado, datos permitidos y tratamiento contractual comprobados |
| LLM/RAG diagnóstico/imagen | Deshabilitado para asistencia; sintéticos y fuentes autorizadas únicamente | Interruptor por capacidad; no PHI ni préstamos restringidos; coste/límites; procedencia y abstención | Finalidad, evidencia clínica, derechos, proveedor/modelo/retención/transferencias y obligaciones IA evaluados |
| Backups y monitorización | Metadatos no clínicos y señales técnicas mínimas | Cifrado, restore sintético, acceso mínimo, retención; no prompts/notas/documentos/URLs sensibles | Responsables y RPO/RTO definidos y medidos; no afirmar anonimato por usar identificadores seudónimos |

## RGPD, proporcionalidad y responsabilidades

Antes de datos reales, identificar responsable/encargados por cada flujo. Documentar finalidad, base del art.6 y, cuando existan datos de salud, condición del art.9 y garantías aplicables; el contrato de la cuenta del médico no autoriza por sí solo tratar información de sus pacientes. Minimización y privacidad por defecto (art.25), contrato de encargado (28), seguridad proporcional (32), evaluación de alto riesgo (35) y transferencias (cap.V) se revisan por tratamiento. No presuponer consentimiento universal ni excepción doméstica por tratarse de un profesional individual. [RGPD, localizadores normativos](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng/); [Comisión, bases jurídicas](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/legal-grounds-processing-data_en).

El proveedor de infraestructura no decide automáticamente la base jurídica sanitaria. La plataforma puede ser responsable de cuentas y encargado u otro rol para otros flujos según quién determine fines y medios. Esa asignación debe describirse antes de habilitar cada flujo real. Esta es una cuestión pendiente de análisis de operaciones, no una atribución cerrada a todas las instalaciones.

DPO y DPIA no se imponen universalmente por el título de médico ni se excluyen por llamar al producto individual. EDPB explica que un único médico no equivale, por ese hecho, a tratamiento a gran escala; una plataforma que agrega usuarios debe evaluarse por volumen, duración, alcance y actividad. La designación de DPO depende de los supuestos aplicables, y una DPIA procede ante probable alto riesgo; revisar además listas nacionales. Si persiste riesgo alto no mitigado, evaluar consulta previa antes del tratamiento. [EDPB, DPO y escala](https://www.edpb.europa.eu/sme/be-compliant/data-protection-officer_en); [EDPB, DPIA](https://www.edpb.europa.eu/topics/accountability-and-compliance-tools/data-protection-impact-assessment_en).

Transparencia, acceso limitado, retención y capacidad de restauración deben incluirse desde diseño. El plan de incidentes debe distinguir notificación del encargado al responsable, evaluación del riesgo y obligaciones de notificar a autoridad/interesados; no declarar toda incidencia automáticamente notificable a todos. [Comisión, privacidad por diseño, seguridad e incidentes](https://commission.europa.eu/law/law-topic/data-protection/information-business-and-organisations/obligations_en).

## Proveedores: contrato y flujo, no bandera

| Opción examinada | Evidencia primaria observada | Consecuencia para decisión pendiente |
|---|---|---|
| Hetzner | Publica modelo DPA art.28, categorías de datos/interesados, lista de subcontratistas y medidas técnicas/organizativas | Revisar entidad contratante, servicio/región elegidos, subencargados, acceso de soporte, copias y salida. No inferir que todos sus servicios resuelven automáticamente salud o transferencias |
| Google Cloud con región UE | CDPA §10 sujeta localización a compromisos específicos del servicio; §11 regula subencargados y notificaciones de cambios | Verificar por producto almacenamiento **y** procesamiento, soporte, logs, backups y mecanismo de transferencia. Elegir Madrid no acredita por sí solo ausencia de acceso fuera del EEE |

[Hetzner, DPA/subcontratistas/TOM](https://docs.hetzner.com/general/company-and-policy/data-protection-at-hetzner/); [Google Cloud, CDPA §§10–11](https://cloud.google.com/terms/data-processing-addendum).

EDPB pide identificar transferencias a terceros países, incluido acceso remoto de entidades externas, y el mecanismo y garantías efectivos. No todo mero riesgo de acceso constituye una transferencia ya realizada; tampoco basta que el disco esté en la UE para descartar acceso remoto. Conservar mapa de flujos, contrato y evaluación antes de habilitarlos. [EDPB, cadenas de tratamiento, noviembre de 2026, §2](https://www.edpb.europa.eu/system/files_en?file=2026-11%2Fedpb-opinions-at-a-glance-230926-processing-chains_en.pdf); [EDPB, guía 05/2021, §13](https://www.edpb.europa.eu/system/files/documents/2023-02/edpb_guidelines_05-2021_interplay_between_the_application_of_art3-chapter_v_of_the_gdpr_v2_en_0.pdf).

No se contrató ni aceptó ningún DPA. No se examinó una cuenta concreta del proveedor ni se certificaron configuraciones reales.

## AI Act: calendario contrastado hoy

La página oficial de la Comisión, actualizada el 27/11/2026, informa entrada en vigor del AI Omnibus el 27/07/2026. Su calendario distingue 02/12/2027 para alto riesgo del anexo III y 02/08/2028 para IA de alto riesgo integrada en productos del anexo I. El Service Desk confirma esos hitos; transparencia art.50 y otras obligaciones tienen fechas anteriores. **No reutilizar como vigente el calendario previo de agosto de 2027.** La aplicabilidad a Emergency requiere determinar sistema, finalidad, rol y condiciones del art.6; usar un LLM no clasifica automáticamente cada función como alto riesgo, ni una revisión médica elimina obligaciones de producto. El aplazamiento de una parte no suspende RGPD/MDR ni autoriza la liberación actual. [Comisión, calendario y Omnibus](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai); [Service Desk, hitos](https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act).

## Nacional frente a institucional

No se eligió jurisdicción. Antes de activar una función real en un país, completar su ficha: ejercicio profesional y verificación cuando corresponda, secreto profesional, documentación/retención aplicable, autoridad competente, condiciones nacionales del dato de salud y lista DPIA. Países ajenos a UE/EEE requieren análisis propio; no presentar esta matriz europea como autorización internacional.

PACS/FHIR, identidad del hospital, comité institucional y estudios multicéntricos se exigen únicamente cuando el flujo, centro o finalidad de investigación dependa realmente de ellos. No bloquean pruebas sintéticas de instalación, identidad o aislamiento. Tampoco el uso individual permite eludir condiciones reales del centro cuando se tratan datos bajo su responsabilidad. Se conserva el límite entre preparación técnica y puesta en servicio.

## Controles que Codex puede ejecutar sin datos reales

- IMP-03: empaquetado con manifiesto SHA, detección de versión, instalación en ruta elegida, actualización atómica y rollback probado; comprobar ausencia de casos/cuentas/secretos en el paquete.
- IMP-04: gateway independiente de servidores de desarrollo, pruebas negativas de autorización, origen, tamaño, tiempo, rutas y registros; respuestas y errores sin eco del cuerpo clínico.
- IMP-05: proveedor OIDC sintético, cookies y sesiones seguras, caducidad, revocación, aislamiento y permisos mínimos. Inicio de sesión no equivale a acreditación profesional.
- IMP-06: esquema limitado a usuarios/preferencias/auditoría técnica; consultas siempre ligadas al sujeto; negativos de acceso cruzado, borrado y restauración sintéticos. No campo remoto libre para casos por defecto.
- IMP-07: entornos locales separados, plantillas sin aplicar a nube, restore verificable, secretos fuera de Git, monitorización sin contenido clínico y retención configurable. Estos controles no requieren comprar servicios.

Estos controles son propuesta de ingeniería derivada del alcance y deben medirse en su implementación; aquí no se registran PASS.

## Límites de lectura y cierre

Se leyeron las páginas oficiales y extractos/localizadores citados; MDCG 2019-11 rev.1 se abrió como PDF de 36 páginas. Las aperturas directas HTML/PDF de EUR-Lex devolvieron comprobación JavaScript/robot; los artículos se contrastaron con resultados indexados oficiales y las explicaciones de Comisión/EDPB. **No se afirma lectura íntegra de la consolidación EUR-Lex ni dictamen jurídico.** Los borradores normativos no son tratados como derecho adoptado.

Pendientes finitos antes de activación: finalidad/alcance por capacidad y clasificación aplicable; país inicial y obligaciones nacionales; roles/base jurídica/retención por flujo; proveedor exacto y DPA/transferencias; controles implementados probados; autorización aplicable. Ninguno se cierra solo por recibir este informe. `CLINICALLY_PENDING` · `NO_GO_CLINICAL_RELEASE`.
