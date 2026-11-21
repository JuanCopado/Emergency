# R4 · Impresión y exportación de farmacología aguda

En la base internacional `ca308af6d51c8ee51128f9756f1536cb77ec3ca0`, el ensayo sintético `amiodarone-arrest-third` mostraba delimitadores de negrita en el texto de monitorización y en su fuente. Se reprodujo en Microsoft Edge sobre Windows 11, tanto en el informe de impresión como en el PDF exportado.

La presentación común de ambos informes convierte encabezados, listas y negritas simples del texto canónico a texto de lectura. Los campos de entrada y la instantánea estructurada conservan el original. Se mantienen literales las expresiones matemáticas, el código y los formatos fuera del alcance del conversor. La huella de revisión de la fuente incorpora el cambio del archivo de implementación como exige el catálogo.

En el mismo caso sintético, las entradas y el resultado estructurado antes y después coincidieron. La vista previa nativa del botón **Imprimir resultado** en Edge mostró cuatro hojas, con dosis y unidad contiguas en la primera. El PDF exportado tuvo cinco páginas, con ambos campos contiguos en la primera. Se comprobaron las dos salidas y pasaron las 15 pruebas de `test_acute_medication_v144.py`.

El alcance es técnico. Se conserva **CLINICALLY_PENDING**.
