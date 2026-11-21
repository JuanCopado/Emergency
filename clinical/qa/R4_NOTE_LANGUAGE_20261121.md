# R4 · Idioma de la nota clínica

La nota usa el idioma de la interfaz. Sus siete plantillas de limitaciones y
las etiquetas de exportación siguen los cuatro idiomas admitidos. La prosa
canónica y el texto libre se conservan. Cambiar idioma después del análisis
invalida la revisión y bloquea exportarlo hasta actualizar el apoyo diagnóstico
explícitamente. El cambio de idioma conserva el borrador y evita recalcular
sin petición.

El ensayo sintético conservó las 60 salidas completas del motor respecto a
`66aec7781bede855f9f4403d461fe6ef119db69d`. Se mantienen pesos, reglas, umbrales,
orden, alertas y estado **CLINICALLY_PENDING**.


La primera revisión de etiquetas ZH reveló que el PDF carecía de glifos CJK.
El candidato final incorpora instancias estáticas regular y negrita de la
fuente oficial Noto Sans SC, con origen fijado, licencia y huellas en
[el manifiesto](../assets/fonts/noto-cjk-manifest.json). Los párrafos latinos
conservan DejaVu. El cambio cubre el chino simplificado probado y conserva el
rechazo de caracteres ajenos a las fuentes disponibles.
