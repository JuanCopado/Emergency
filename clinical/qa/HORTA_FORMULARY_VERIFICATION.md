# Hospital da Horta — verificación local de fármacos críticos

## Regla
Esta ficha es el gate local para convertir una referencia nacional/RCM en un estándar operativo del Hospital da Horta.

**No marcar un fármaco como `verified` solo porque exista en INFARMED/FNM.** Deben constar producto real, RCM y estándar local.

## Campos obligatorios por fármaco

| Campo | Requerido |
|---|---|
| Principio activo | sí |
| Nombre comercial / fabricante | sí |
| Nº de registro / RCM | sí |
| Presentación y concentración de ampolla/vial | sí |
| Base / sal / cantidad equivalente declarada | sí |
| Diluyente(s) permitidos | sí |
| Volumen final estándar | sí |
| Concentración final estándar | sí |
| Estabilidad tras preparación | sí |
| Protección de luz / material especial | si aplica |
| Línea periférica/central y condiciones | sí |
| Compatibilidades críticas / incompatibilidades | sí |
| Entrada en biblioteca de bomba | sí/no + nombre |
| Límites de dosis/rate configurados | sí |
| Protocolo/servicio propietario | sí |
| Farmacéutico revisor | sí |
| Médico revisor | sí |
| Fecha de revisión | sí |

## Prioridad 1 — vasoactivos/inotrópicos

### Noradrenalina
- Producto:
- Nº registro / RCM:
- Ampolla/vial:
- La etiqueta expresa: base / sal / equivalente:
- Diluyente:
- Volumen final:
- Concentración final:
- Estabilidad:
- Acceso periférico permitido:
- Condiciones acceso periférico:
- Concentración para acceso periférico:
- Extravasación:
- Smart-pump:
- Revisor farmacia:
- Revisor clínico:
- Fecha:

### Adrenalina
(mismos campos)

### Vasopresina / argipresina
(mismos campos)

### Dopamina
(mismos campos)

### Dobutamina
(mismos campos)

### Amiodarona
(mismos campos; añadir material de línea/filtro si aplica)

### Isoprenalina
(mismos campos)

## Prioridad 2 — sedación/analgesia UCI

### Propofol
- Producto:
- 10 mg/mL / 20 mg/mL / otra:
- Presentación:
- Uso directo o dilución:
- Tiempo máximo de sistema abierto:
- Cambio de línea:
- Lípidos/nutrición:
- Smart-pump:
- Revisor farmacia:
- Revisor clínico:
- Fecha:

### Dexmedetomidina
- Producto:
- Concentrado o ready-to-use:
- Concentración de origen:
- Concentración final:
- Diluyente:
- Estabilidad:
- Smart-pump:
- Revisor farmacia:
- Revisor clínico:
- Fecha:

### Midazolam
(mismos campos)

### Fentanilo IV
(mismos campos)

### Remifentanilo
- Producto:
- Vial 1/2/5 mg:
- Reconstitución:
- Dilución final:
- Concentración final estándar:
- Estabilidad:
- Smart-pump:
- Revisor farmacia:
- Revisor clínico:
- Fecha:

## Regla de promoción local
Solo después de completar todos los campos críticos y registrar revisores podrá cambiarse el estado del fármaco en `localization-portugal-azores.json` a `verified`.

La promoción local **no cambia automáticamente** el estado clínico del módulo de yellow a green.
