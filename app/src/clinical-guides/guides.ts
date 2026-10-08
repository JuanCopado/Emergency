import type { ClinicalGuide } from './types';

export const clinicalGuides: ClinicalGuide[] = [
  {
    id: 'vf-pvt',
    title: 'FV / TV sin pulso',
    subtitle: 'Algoritmo rápido de parada cardiaca con ritmo desfibrilable',
    sourceModule: 'adult-cardiac-arrest',
    sourcePath: 'clinical/modules/cardiovascular.md',
    status: 'yellow',
    reviewedAt: '2026-10-08',
    references: ['ERC/RCUK 2025', 'Módulo canónico adult-cardiac-arrest'],
    steps: [
      { title: '1. Confirmar parada', body: 'Inconsciencia con respiración ausente o anormal. Activar equipo de reanimación e iniciar RCP de alta calidad sin demora.' },
      { title: '2. Conectar desfibrilador', body: 'Minimizar interrupciones. Clasificar el ritmo como desfibrilable (FV/TV sin pulso) o no desfibrilable.' },
      { title: '3. Choque', body: 'Administrar un choque y reanudar inmediatamente RCP durante 2 minutos. Los choques apilados quedan reservados a situaciones seleccionadas presenciadas/monitorizadas con desfibrilador disponible.' },
      { title: '4. Energía', body: 'Bifásica rectilínea o exponencial truncada: primer choque al menos 150 J. Pulsed biphasic: 130–150 J. Escalar si el primer choque falla y el equipo lo permite.' },
      { title: '5. Fármacos', body: 'Adrenalina 1 mg IV tras el tercer choque y cada 3–5 min. Amiodarona 300 mg IV tras tres choques; 150 mg adicional tras cinco choques.' },
      { title: '6. Acceso', body: 'Intentar acceso IV primero. Si no se consigue rápidamente en dos intentos, utilizar IO.' },
      { title: '7. Vía aérea y capnografía', body: 'Priorizar compresiones continuas y ventilación eficaz sin hiperventilar. Usar capnografía con vía aérea avanzada.' },
      { title: '8. Causas reversibles', body: 'Buscar y tratar hipoxia, hipovolemia, alteraciones metabólicas, hipotermia, neumotórax a tensión, taponamiento, tóxicos y trombosis pulmonar/coronaria.' },
      { title: '9. ROSC', body: 'Tras ROSC: controlar oxigenación/ventilación, estabilizar hemodinámica, ECG de 12 derivaciones y evaluación dirigida de la causa.' },
    ],
    stopPoints: [
      'No retrasar compresiones por monitor, acceso IV o procedimientos de vía aérea.',
      'POCUS solo durante pausas planificadas y sin prolongarlas.',
      'No usar un único dato aislado como criterio de finalización.'
    ],
    confirmation: ['Ritmo reevaluado según ciclo ALS', 'RCP reanudada inmediatamente tras cada choque', 'Causas reversibles abordadas', 'Si ROSC: transición inmediata a cuidados postparada']
  },
  {
    id: 'asystole-pea',
    title: 'Asistolia / AESP',
    subtitle: 'Algoritmo rápido de parada cardiaca con ritmo no desfibrilable',
    sourceModule: 'adult-cardiac-arrest',
    sourcePath: 'clinical/modules/cardiovascular.md',
    status: 'yellow',
    reviewedAt: '2026-10-08',
    references: ['ERC/RCUK 2025', 'Módulo canónico adult-cardiac-arrest'],
    steps: [
      { title: '1. Confirmar parada', body: 'Iniciar RCP de alta calidad y conectar monitor/desfibrilador sin retrasar compresiones.' },
      { title: '2. Clasificar ritmo', body: 'Confirmar ritmo no desfibrilable: actividad eléctrica sin pulso o asistolia.' },
      { title: '3. Adrenalina', body: 'Administrar adrenalina 1 mg IV tan pronto como sea posible y repetir cada 3–5 min mientras continúa ALS.' },
      { title: '4. Acceso', body: 'Intentar IV primero; utilizar IO si no se obtiene rápidamente en dos intentos.' },
      { title: '5. RCP', body: 'Continuar ciclos de RCP de 2 minutos con interrupciones mínimas y reevaluación del ritmo.' },
      { title: '6. Vía aérea', body: 'Ventilar eficazmente sin hiperventilar. Usar capnografía de onda si existe vía aérea avanzada.' },
      { title: '7. Causas reversibles', body: 'Buscar y tratar hipoxia, hipovolemia, alteraciones metabólicas, hipotermia, neumotórax a tensión, taponamiento, tóxicos y trombosis.' },
      { title: '8. Si cambia a FV/TV sin pulso', body: 'Pasar inmediatamente a la rama desfibrilable.' },
      { title: '9. ROSC', body: 'Iniciar cuidados postparada con control respiratorio, hemodinámico, ECG y tratamiento de la causa.' },
    ],
    stopPoints: [
      'No desfibrilar asistolia/AESP.',
      'No retrasar adrenalina en ritmos no desfibrilables.',
      'No prolongar pausas para POCUS o procedimientos.'
    ],
    confirmation: ['RCP continua de alta calidad', 'Adrenalina administrada según algoritmo', 'Causas reversibles evaluadas', 'Transición correcta si el ritmo se hace desfibrilable o aparece ROSC']
  },
  {
    id: 'coma',
    title: 'Coma / alteración del nivel de conciencia',
    subtitle: 'Evaluación inicial y prioridades en urgencias',
    sourceModule: 'altered-consciousness',
    sourcePath: 'clinical/modules/neurologic.md',
    status: 'yellow',
    reviewedAt: '2026-10-08',
    references: ['Módulo canónico altered-consciousness'],
    steps: [
      { title: '1. ABC', body: 'Estabilizar vía aérea, respiración y circulación.' },
      { title: '2. Glucosa', body: 'Comprobar glucemia de forma inmediata.' },
      { title: '3. Diagnósticos tiempo-dependientes', body: 'Considerar hipoxia/hipercapnia, shock, crisis epiléptica, ictus/hemorragia, infección, tóxicos, enfermedad metabólica y trauma.' },
      { title: '4. Historia dirigida', body: 'Obtener información colateral y revisar medicación cuando sea posible.' },
      { title: '5. Exploración', body: 'Evaluar pupilas, exploración neurológica y temperatura.' },
      { title: '6. Pruebas dirigidas', body: 'Seleccionar laboratorio, ECG, imagen y toxicología según los hallazgos clínicos.' },
      { title: '7. Antídotos', body: 'Administrar antídotos urgentes solo cuando estén indicados y con plan de protección/rescate de vía aérea.' },
      { title: '8. Reevaluación', body: 'Reevaluar tras cada intervención.' },
      { title: '9. Destino', body: 'La alteración inexplicada o persistente requiere ingreso monitorizado.' },
    ],
    stopPoints: [
      'No atribuir el coma a una sola causa antes de excluir amenazas reversibles inmediatas.',
      'No administrar antídotos sin indicación clínica y plan de rescate.',
      'No omitir reevaluación después de cada intervención.'
    ],
    confirmation: ['ABCs estabilizados', 'Glucosa conocida', 'Etiologías críticas consideradas', 'Plan diagnóstico y de monitorización definido']
  },
];

export const getClinicalGuide = (id: string) => clinicalGuides.find((guide) => guide.id === id);
