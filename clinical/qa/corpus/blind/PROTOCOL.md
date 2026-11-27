# R5-2 · corpus ciego independiente · protocolo (PROPUESTO)

**22 de noviembre de 2026 · Estado global `CLINICALLY_PENDING` (129 GREEN / 2 YELLOW / 0 RED)**

Decisión del propietario, Dr. Juan Copado Ceballos, comunicada en la instrucción R12 de la sesión del 22/11/2026: `DEC-CLIN-R8-06B: SÍ. Corpus ciego R5-2 independiente, cuatro estratos, siete clases y adjudicación. Ninguna regex nueva autorizada.` Este documento solo prepara el protocolo y las herramientas; no se ha construido ningún corpus, no hay adjudicadores designados y no se modifica el filtro. R5-2 sigue **abierto**.

## Qué es y qué no es

- Es una medición **ciega e independiente** del filtro de lenguaje tranquilizador vigente sobre fotografías de piel y heridas, para saber cuánto falla antes de decidir nada.
- **No** autoriza expresiones nuevas, ampliar el léxico, tratar homoglifos ni cambiar el ámbito del filtro. Cualquier cambio exige decisión médica expresa posterior.
- **No** es validación clínica ni sustituye al corpus sintético R8 (`../r8_reassurance_synthetic_corpus_v0.json`), que sigue siendo solo regresión técnica con etiquetas de construcción.

## Estratos y clases

- **Tres lenguas base:** español, portugués e inglés.
- **Cuatro estratos de evaluación:** `es-ES`, `pt-PT`, `pt-BR`, `en` (el portugués se evalúa en sus dos variedades).
- **Portugués:** redacción conforme al Acuerdo Ortográfico de 1990 (AO90), con una ortografía común; se **conservan las diferencias terminológicas regionales** cuando sean relevantes para el sentido clínico (p. ej. el vocabulario que difiere entre Portugal y Brasil). No se «normaliza» una variedad a la otra, y una redacción de pt-BR no sustituye a la de pt-PT.
- **Siete clases de construcción:** `explicit_reassurance`, `implicit_paraphrase`, `negated_warning`, `neutral_descriptive`, `unicode_variant`, `homoglyph`, `contradiction` (las mismas que el corpus R8).
- El tamaño por celda idioma × clase **lo fija el propietario antes de construir**. Referencia informativa: con *n* textos tranquilizadores por idioma y ninguna omisión, la cota superior del 95 % de la tasa de omisión es aproximadamente 3/*n* (regla de tres); con omisiones observadas, intervalo exacto (Clopper-Pearson).

## Roles e independencia

| Rol | Condición |
|---|---|
| Custodio del corpus | Persona o grupo **ajeno al desarrollo del filtro y de esta aplicación**. Guarda corpus, claves y resultados fuera del repositorio |
| Redactores del corpus | No pueden haber visto el léxico del filtro (`_REASSURANCE`) ni el corpus R8 al redactar |
| Adjudicadores | Al menos **dos por idioma**, competentes en ese idioma y en la materia; un **tercero dirimente** por idioma. Nadie adjudica un texto que haya redactado |
| Desarrollo (Claude, Antigravity, otros) | **No ve textos ni etiquetas** del corpus ciego. Recibe solo el manifiesto (recuentos y hash) y los resultados agregados |

## Aislamiento (reglas, con comprobación automática)

1. Corpus, paquetes, claves y adjudicaciones **no se guardan en el repositorio**. Las herramientas (`clinical/scripts/blind_corpus_tools.py`) **no acceden al sistema de archivos**: leen la entrada estándar y escriben la salida estándar, de modo que el custodio decide dónde viven los datos (con redirecciones de shell, fuera del repositorio). Una prueba falla si el módulo llega a abrir, leer o escribir un archivo.
2. El repositorio contiene **solo este protocolo y las herramientas**; una prueba falla si aparece otro archivo en esta carpeta.
3. Ningún script del producto, del filtro ni de la interfaz importa ni menciona las herramientas del corpus ciego (prueba automática).
4. El corpus se **congela** antes de adjudicar: se calcula el hash (`manifest`) y el compromiso se registra en el repositorio **sin texto**.
5. **Regla de quemado:** si se cambia el filtro tras ver resultados por ítem, o se filtra cualquier texto del corpus al desarrollo, ese corpus deja de ser ciego y debe sustituirse por uno nuevo.

## Procedimiento

1. El custodio construye el corpus con los campos exactos `id`, `lang`, `class`, `text`. Sin etiquetas de ingeniería (`label`, `expected`…): la herramienta las rechaza.
2. `manifest` (entrada: el corpus): recuentos por idioma, clase y celda, celdas vacías y hash de los bytes exactos. Es lo único que sale del custodio antes de la medición.
3. `packets` (entrada: el corpus; salida: `{packet, key}`, que el custodio separa): un paquete por adjudicador (orden aleatorio reproducible, códigos opacos, **sin clase ni etiqueta**) y un archivo de claves que solo conserva el custodio.
4. Cada adjudicador responde, por texto y sin ver la salida del filtro, una pregunta cerrada (propuesta; el propietario puede enmendarla): **¿el texto transmite al lector que la lesión es inocua o que no requiere valoración?** `reassures` / `does_not_reassure` / `cannot_decide`.
5. `agreement` exige `{corpus, adjudications, role_manifest}` en un solo JSON. Devuelve porcentaje de acuerdo y kappa de Cohen entre los dos adjudicadores primarios declarados para cada idioma y lista de ítems que van al dirimente (desacuerdo o `cannot_decide`). Etiqueta final: acuerdo de los dos primarios; si no, el dirimente; si sigue sin decidirse, `unresolved` (se informa, no se fuerza). La comprobación formal de roles no acredita independencia humana.
6. **Medición única** del filtro vigente, por el custodio, sobre las etiquetas finales: omisiones y falsos avisos por idioma y clase con intervalos exactos. Se informa por versión del filtro y por hash del corpus.
7. Resultado: informe agregado al propietario. Las conclusiones y cualquier cambio son decisión médica; el informe no propone expresiones.

## Manifiesto de asignación del circuito

`role_manifest` tiene los campos exactos `schema` (`blind-corpus-roles-v1`), `corpus_canonical_sha256`, `people`, `roles` y `panels`. Cada entrada de `people` contiene un `id` estable ASCII en minúsculas (3–64 caracteres, patrón `[a-z][a-z0-9_-]{2,63}`) y una `identity_ref` opaca al registro de identidad/conflictos del custodio. Los IDs y referencias normalizadas NFKC, sin espacios periféricos y sin distinguir mayúsculas, no pueden duplicarse. No se guardan nombres ni este registro en el repositorio.

Los cuatro roles (`author`, `evaluator`, `custodian`, `adjudicator`) requieren integrantes registrados y mutuamente distintos; al menos uno por rol y tres adjudicadores. Toda persona registrada debe tener un único rol. `panels` declara por cada lengua presente dos IDs `primary` y un ID `tiebreaker`, tres adjudicadores distintos. Se pueden reutilizar adjudicadores entre lenguas si el custodio acredita su competencia; también se permiten paneles diferentes. Los votos solo pueden proceder del panel del idioma del texto. `--primary` es opcional y, si se proporciona por compatibilidad, debe coincidir con todos los paneles. El subcomando histórico `roles` es solo una comprobación preliminar de listas, no sustituye este manifiesto obligatorio.

El custodio vincula el manifiesto a `canonical_corpus_sha256(corpus)`: JSON UTF-8, claves ordenadas, separadores `,`/`:`, caracteres Unicode literales y sin NaN. Este compromiso canónico es distinto del hash de bytes exactos que sigue devolviendo `manifest(raw)`; ambos conservan su nombre y finalidad. La salida de `agreement` declara `FORMAL_CONSISTENCY_ONLY_NOT_HUMAN_INDEPENDENCE` y no expone las referencias de identidad. El custodio comprueba por separado identidad real, competencia por idioma, ausencia de conflictos, no exposición al filtro y autorizaciones. Un validador no puede detectar una persona registrada con dos identidades falsas ni certifica esas comprobaciones.

Este circuito mide el filtro de lenguaje tranquilizador. No sustituye el corpus de notas clínicas con sus referencias independientes de aserción textual, prioridad t0 y diagnóstico final. No se han nombrado revisores ni creado corpus en esta actualización.

## Pendiente de decisión o de personas

- Tamaño por celda y criterio de aceptación de la concordancia (umbral de kappa).
- Designación del custodio, de los redactores, de los adjudicadores y del dirimente por idioma. `DEC-CLIN-R7-01` (portugués como estrato) debe resolverse antes de adjudicar pt-PT y pt-BR.
- Redacción médica definitiva de la pregunta de adjudicación.
- Dónde se custodia el material fuera del repositorio.
