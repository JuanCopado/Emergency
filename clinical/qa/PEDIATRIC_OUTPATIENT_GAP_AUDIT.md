# PEDIATRIC OUTPATIENT MEDICATIONS — GAP / EXCLUSION AUDIT

Fecha: 04/10/2026
Rama: `v1.38-pediatric-outpatient-medications`

## Objetivo
Definir qué queda deliberadamente fuera del formulario automático para evitar que "exhaustivo" se interprete como "todo fármaco pediátrico posible".

## Cobertura actual
El registro contiene **89 regímenes diagnosis-specific** y cubre:
- antibióticos orales frecuentes y varias alternativas por alergia/resistencia;
- analgesia/antitermia;
- antiemesis seleccionada;
- antihistamínicos orales;
- rescate y controladores de asma por edad/step;
- eczema, impétigo, micosis, escabiosis y pediculosis;
- ORS y estreñimiento;
- antiparasitarios seleccionados;
- antivirales de uso ambulatorio seleccionado;
- ENT/oftalmología ambulatoria;
- rinitis/conjuntivitis alérgica;
- migraña;
- anafilaxia al alta.

## Exclusiones deliberadas

### Antieméticos
No se añaden de forma rutinaria metoclopramida, domperidona, proclorperazina ni otros antieméticos sedantes/dopaminérgicos como pauta domiciliaria genérica. Su beneficio pediátrico ambulatorio es limitado/indicación-dependiente y sus efectos adversos (extrapiramidales, QT, sedación u otros) desaconsejan una entrada universal de alta.

### Reflujo
No se añaden supresores de ácido para regurgitación fisiológica del lactante. PPI/H2 solo deben incorporarse con diagnóstico de GORD/indicación definida, edad, producto y pauta verificadas; no como tratamiento empírico de "reflujo".

### Antibióticos
No existe una tabla universal por antibiótico. Cada pauta permanece ligada a diagnóstico, alergia, gravedad, función renal, epidemiología/resistencia y fuente. Infecciones graves, lactantes de alto riesgo, sospecha de meningitis/sepsis, enfermedad orbital profunda, abscesos que requieren drenaje y fracaso de tratamiento oral remiten al pathway de urgencias/especialista.

### Dermatología
No se añaden corticoides tópicos muy potentes ni inmunomoduladores sistémicos sin especialista. Tinea capitis/onicomicosis y otras micosis que requieren terapia sistémica deben incorporarse solo con producto/monitorización y fuente específica.

### Antiparasitarios
No se unifican intervalos discrepantes entre guías. Por ejemplo, el intervalo de repetición de ivermectina para escabiosis varía entre fuentes; el formulario conserva permethrin como pauta tópica principal y no crea una regla oral híbrida.

### Asma
No se mezclan SABA-only y AIR/MART. Cada dispositivo/strength/step queda separado. El motor no sustituye un inhalador por otro aunque ambos contengan budesonide/formoterol.

### Migraña
No se añaden opioides. Preventivos crónicos de migraña quedan fuera de este módulo de alta de urgencias salvo que exista una ruta pediátrica especializada y seguimiento.

### Productos Portugal/Azores
Una presentación documentada por INFARMED no prueba stock actual en Azores. El cálculo de mL exige la concentración exacta del producto realmente seleccionado/dispensado.

## Pendientes razonables
1. Revisión humana pediatría/farmacia de las 89 entradas.
2. Reconciliación de productos actuales en INFOMED y, por separado, disponibilidad local Azores.
3. Añadir únicamente fármacos adicionales de alta prevalencia/valor clínico que superen el filtro beneficio-riesgo y tengan fuente pediátrica/SmPC clara.
4. Casos clínicos de regresión por diagnóstico, alergia, obesidad, insuficiencia renal y concentraciones alternativas.
5. Mantener `yellow` hasta completar esos gates.
