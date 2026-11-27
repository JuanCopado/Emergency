# R88/G05 — preparación operativa verificada

Trabajo nuevo de este corte: verificados nuevamente 10 originales históricos, 20 copias de preasignación y 30 referencias semánticas a fichas existentes, sin regenerarlas. Se conservan los 19 contratos y MED-DEC-R46-01/02. Se han materializado el contrato de roles con identificadores estables y personas por asignar, el plan metodológico paramétrico sin tamaño ni márgenes inventados, el registro de campos, usos y retención, y las condiciones específicas de PTBR-PIX. Es preparación: no se inicia un estudio, adjudicación, distribución de paquetes o cambio del candidato.

## Conciliaciones documentales concretas

- G05 dispone de los identificadores canónicos G05-01..06 en `docs/coordination/r5-g05-20261126/G05_REQUISITOS.json`: consumidor, derechos, privacidad, integridad externa, liberación y trazabilidad, y PTBR-PIX. Los seis ejes inferidos de PR119 se corresponden con estos identificadores; no se sustituyen silenciosamente. Campos y licencias → G05-02; almacenamiento y privacidad → G05-03; plataforma → G05-01/03; responsables → G05-01/05.
- El aprobador clínico ya es el Dr. Juan Copado Ceballos. Faltan los otros nombramientos reales. No falta designar al propietario ni una firma obligatoria de Farmacia. La aceptación final del propietario no sustituye a dos jueces independientes.
- SCA: existe el ejecutable externo en Descargas, con recibo y hash propios. SHA `1d219bdd…` identifica `study.json`, no el ejecutable. El ensayo sintético no se repite ni se atribuye al candidato actual; el script no se ha ejecutado en este corte.
- El corpus R5-2 histórico, cuatro estratos por siete clases, mide el filtro de lenguaje tranquilizador. No acredita las tres referencias de nota clínica: aserción, prioridad t0 y diagnóstico final. Se mantienen finalidades y autorizaciones separadas. HIGH no es diagnóstico ni probabilidad calibrada.
- Los 10 archivos y 20 copias son preparación histórica. No se presentan como 30 admisiones ni como 10 casos reservados. La matriz diagnóstica conserva 16 referencias requeridas y 14 N/A, fuera de los paquetes de los revisores. No se han copiado claves ni respuestas esperadas.
- El servidor T06 escribe recibos y registros sintéticos y no define un plazo de retención o limpieza automática de estos. `cache_dir=None` no acredita ausencia de toda persistencia. En el cliente T06 no se observó persistencia. Se documenta el límite sin fijar plazos por inferencia.

## Base de diseño y límites

La [guía estadística FDA 2007](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/statistical-guidance-reporting-results-studies-evaluating-diagnostic-tests-guidance-industry-and-fda) recomienda definir población y referencia independiente e informar la incertidumbre. La comparación con un método que no sea referencia debe evitar presentar acuerdo como sensibilidad o especificidad. Las fórmulas propuestas en el contrato son orientaciones matemáticas condicionadas, no tamaños aprobados. El muestreo repetido de factores humanos conserva la agrupación por participante y R20. Las 28 celdas son diseño, no resultados. La exactitud diagnóstica exige casos reservados y referencia clínica independiente.

Derechos por uso: se consultaron [NCBI](https://www.ncbi.nlm.nih.gov/home/about/policies/) y el [copyright oficial de Europe PMC](https://dev.europepmc.org/Copyright). No se infiere una licencia uniforme del acceso gratuito; resúmenes y texto completo no se autorizan por defecto. La URL canónica de Europe PMC devolvió 403. NVD no entregó texto legible en la consulta vigente: se conserva R6 como evidencia histórica y no se afirma una nueva lectura legal de NVD.

Los bloqueos reales y sus condiciones de salida figuran en `R88_PENDIENTES_OPERATIVOS.json`. Hay cero decisiones médicas nuevas maduras; el carril científico consolida la comprobación de MED-RES-PROT-01. No se construyó un corpus, no se reservaron casos, no se nombraron personas, no se concedieron permisos ni se cambió `last_checked`.

CLINICALLY_PENDING · NOT_FROZEN_NOT_VALIDATED · NO_GO_CLINICAL_RELEASE.
