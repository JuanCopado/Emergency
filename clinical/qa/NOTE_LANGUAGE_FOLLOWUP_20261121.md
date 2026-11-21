# R4 · Idioma de la nota clínica

Base internacional `66aec7781bede855f9f4403d461fe6ef119db69d`. La interfaz pasa a la nota su idioma seleccionado entre español, portugués, inglés y chino. Siete mensajes automáticos de limitación usan ese idioma. El portugués conserva sus literales previos. El esquema, pesos, umbrales, orden, diagnóstico canónico y contenido introducido se conservan.

Al cambiar de idioma después de analizar, el resultado queda desactualizado y se invalida la revisión de exportación. Aunque se marque de nuevo la revisión, la exportación espera una nueva actualización diagnóstica solicitada por el usuario. La aplicación conserva el borrador y evita sustituir el análisis mediante una petición automática.

El exportador localiza etiquetas fijas en inglés y chino, además de las etiquetas portuguesas y españolas previas. Los campos clínicos y el texto libre se copian literalmente. Los textos de las reglas clínicas conservan su idioma canónico. La primera revisión detectó una regresión de glifos en el PDF chino. La revisión final incorpora fuentes CJK portátiles verificadas y conserva el rechazo explícito de caracteres que ninguna fuente cubre. JSON y DOCX conservan Unicode. La solución y su procedencia figuran en [el seguimiento de fuentes](R4_NOTE_LANGUAGE_20261121.md).

Pruebas focales en Windows: 35/35 de interfaz (incluido el cambio de idioma después del análisis), 12/12 de observaciones y 4/4 regresiones de localización y fuentes, tipos y lint. Las regresiones crean y leen DOCX y PDF en los cuatro idiomas, comprueban el texto chino mixto y verifican que un carácter no disponible sigue produciendo un rechazo explícito. Estado global `CLINICALLY_PENDING`.
