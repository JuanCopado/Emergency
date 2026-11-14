# Revisión del PNT adjunto de perfusiones UCI ·14/11/2026

**Aclaración posterior del propietario:** Empressin1UI/mL seleccionado localmente, tabla propia; uso inmediato y recambio local≤24h, con límites Lipuro6/12h. La comparación original de0,8UI/mL y los plazos de fabricante quedan como antecedentes, no como la selección local actual. Véase `LOCAL_INFUSION_DECISIONS_2026-11-14.md`.

**Sí ayuda:** concreta las17 recetas candidatas, resuelve las selecciones
propuestas de milrinona y ketamina y permite comprobar volúmenes de origen.
El archivo original se ha leído completo y no se ha modificado. Su título y
lista de organizaciones no sustituyen las referencias concretas por producto.
Las firmas y fecha de entrada en vigor están vacías; los nombres ya declarados
por el propietario se conservan aparte. No se firma ni se publica el PNT.

## Correcciones necesarias

1. **Noradrenalina:**25mg base/250mL =100µg base/mL;50mL de la presentación
   declarada contienen25mg base. La aritmética es correcta. Su estabilidad24h
   a esta concentración y en ese sistema no queda probada por CIMA62002.
   La hiperglucemia no acredita por sí sola un diluyente alternativo.
2. **Empressin:** el PNT ofrece1UI/mL o0,8UI/mL; son dos tablas de bomba distintas.
   Se conserva la referencia CIMA0,8UI/mL;1UI/mL queda como propuesta sin aval
   trasladado de otro producto. La ficha03/2026 exige diluir/usar inmediatamente.
3. **Recambio24h:** retirar la regla universal del apartado5. Estabilidad química,
   almacenamiento microbiológico y permanencia del sistema conectado son
   comprobaciones distintas. Las fichas de adrenalina/Ketolar y Empressin
   consultadas no acreditan el plazo genérico del PNT.
4. **Propofol:** el límite de6h contrastado es para Lipuro1% diluido. No se debe
   presentar como obligación universal por trasvasar propofol sin diluir.
   La pauta12h del sistema sin diluir sigue siendo específica del producto.
5. **Cambios de concentración:** a la misma dosis, fentanilo50µg/mL necesita
   una quinta parte del flujo del ejemplo10µg/mL; propofol20mg/mL necesita
   la mitad del ejemplo10mg/mL. No copiar las velocidades antiguas.
6. **Compatibilidad/material:** no quedan demostradas todas las combinaciones
   en Y ni todos los límites periféricos32µg/mL/18G. Concentración y material
   de cada combinación deben constar. Lo no estudiado no equivale a precipitación
   demostrada, aunque no deba mezclarse sin respaldo.
7. **Detalles restantes:** nombrar el producto real cuando cambia las condiciones
   de uso; confirmar el suministro de hidromorfona/Giapreza; expresar siempre
   volumen final —especialmente en la receta de Giapreza— y convención base/sal.

## Qué se ha incorporado

Las17 recetas del PNT se conservan como propuestas de concentración en
`INFUSION_PRODUCT_RECONCILIATION_2026-11-14.json`, sin convertirlas en órdenes
ni autorizar automáticamente la bomba. La tabla compañera actualiza los
pendientes: ya no solicita las recetas que este archivo aporta.
Las fuentes primarias concretas, la revisión de cada producto y los seis
puntos de control están en ese expediente. Los módulos conservan YELLOW;
global91GREEN/40YELLOW/0RED y CLINICALLY_PENDING.19 contratos bloqueados intactos.

QA PASS:673 Python,434 frontend,4/4 guías y7/7 controles;9 nuevas regresiones de producto/unidades. Detalle: `INFUSION_PRODUCT_RECONCILIATION_QA_2026-11-14.json`. No se ha ejecutado navegador nuevo.
