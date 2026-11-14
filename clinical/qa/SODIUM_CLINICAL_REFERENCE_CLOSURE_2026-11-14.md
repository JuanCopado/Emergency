# Sodio — cierre de revisión clínica14/11/2026

**Módulo sodium-emergencies:GREEN de referencia clínica.** Registro actual:
**113GREEN/18YELLOW/0RED**. Estado global CLINICALLY_PENDING.

## Confirmación local conservada

El propietario reconfirma **NaCl al3% preparado por enfermería** según la receta
ya aportada de NaCl20% ySF0.9%;también dispone de glucosa5%,SF0.9%,SF0.45% y agua
destilada si precisa. Se registra como declaración local;no se vuelven a pedir
esos datos. La masa calculada de las mezclas100/250/500mL da3.001%,aproximadamente
3%,con los volúmenes finales reales especificados. No se altera la receta.

La disponibilidad de agua destilada no establece que cualquier agua sea apta
para uso parenteral:solo agua estéril para preparaciones inyectables como
diluyente compatible;nunca perfusión de agua sola. No se crea una receta nueva
con los otros fluidos ni se certifica indistintamente su intercambiabilidad.

## Conciliación clínica

Se conservan la pauta adulta publicada de bolos de3%,los límites acumulados,
la vigilancia del sodio/diuresis y el rescate seleccionado por especialistas.
Se aclaran la duración finita del bolo,la necesidad de reevaluación y las
precauciones para seguimiento con distintas plataformas analíticas. Se añade
la distinción entre volumen preparado y volumen que debe administrarse.

La evidencia adulta2026 de hipernatremia se incorpora con sus limitaciones:
una emulación observacional no es un ensayo aleatorizado y la síntesis reciente
muestra heterogeneidad. No se adopta una velocidad universal más rápida,ni se
extiende el resultado a niños. El documento europeo recuperado continúa
rotulado borrador;no se presenta como sustitución final de la pauta publicada.

## Alcance del verde

El estadoGREEN corresponde al marco clínico y la aritmética revisados.La
preparación/ disponibilidad local quedan reconfirmadas por el propietario,con
esa procedencia explícita;no se inventa una auditoría presencial de producto,
recipiente,vía o estabilidad. Los controles rutinarios de preparación y
administración permanecen activos. El módulo puede estarGREEN sin que el
sistema marque automáticamente como comprobados los datos de un paciente.

## QA

PASS:710 pruebas Python,434 frontend,4 guías y7 controles;6 regresiones nuevas.
El API sigue bloqueando un producto/protocolo no verificado,ausencia de
monitorización/rescate,límite de corrección alcanzado o respuesta inicial ya
obtenida. Mantiene la representación de bolo con volumen y duración;la cantidad
por hora no se convierte en una perfusión continua.313 archivos protegidos,
130 registros ajenos y19 contratos bloqueados sin cambios.Sin navegador nuevo.

## Fuentes y registros

- SfE emergency hyponatraemia2022: https://www.endocrinology.org/media/xhrhxhxm/emergency-management-of-severe-and-moderately-severely-symptomatic-hyponatraemia-in-adult-patients-2022.pdf — published adult bolus, supervision, analytical platform and overcorrection precautions
- European published hyponatraemia guideline2014: https://academic.oup.com/ejendo/article/170/3/G1/6668028 — correction limits and expert-directed rescue; primary indexed recommendations; direct publisher fetch blocked
- ESE published guideline directory: https://www.ese-hormones.org/publications/directory/ese-clinical-guideline-for-the-management-of-hyponatraemia/ — published2014 guideline; no final2026 replacement established
- ESE/ERA draft for review: https://www.ese-hormones.org/media/nfca3mga/hyponatraemia-joint-guideline-draft-for-review.pdf — draft tracked; not relabelled final or substituted into selected emergency regimen
- Adult severe hypernatraemia target-trial emulation: https://pubmed.ncbi.nlm.nih.gov/41240509/ — primary observational analysis;online2025-11-15,print April2026; abstract indexed
- Adult hypernatraemia correction meta-analysis6November2026: https://pubmed.ncbi.nlm.nih.gov/42989584/ — original synthesis of observational studies; indexed primary abstract; no uniform causal correction target
- CIMA sterile water for injections72539: https://cima.aemps.es/cima/dochtml/ft/72539/FT_72539.html — water is a preparation diluent;never infuse alone;not identification of locally supplied water
- SfE inpatient cranial diabetes insipidus guidance2018: https://pmc.ncbi.nlm.nih.gov/articles/PMC6013691/ — fluid sodium content and restoring intravascular volume before free water in the relevant adult DI context

Registro: `SODIUM_CLINICAL_REFERENCE_CLOSURE_2026-11-14.json`. QA: `SODIUM_CLINICAL_REFERENCE_CLOSURE_2026-11-14_QA.json`.
