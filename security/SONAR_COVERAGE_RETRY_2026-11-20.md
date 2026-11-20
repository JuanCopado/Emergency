# Sonar: entrega de cobertura tras reintentos parciales

Fecha: 20/11/2026. Base: `21defd4efc4f1b6d15ddb28c655772ca3e4b8a0c`
(PR48), rama internacional v1.44. Cambio exclusivamente técnico.

## Fallo observado

En [Security and quality 44787980529](https://github.com/JuanCopado/Emergency/actions/runs/44787980529),
el primer intento publicó `test-coverage-44787980529-1` y la cobertura T06.
T05 falló en el recorrido de navegador; el reintento de T05 terminó correctamente.
El [trabajo Sonar del segundo intento](https://github.com/JuanCopado/Emergency/actions/runs/44787980529/job/136473902017)
buscó `test-coverage-44787980529-2`, que no existía. El escáner quedó sin ejecutar.
La misma dependencia incorrecta del intento del consumidor afectaba a las
descargas de cobertura T05 y T06.

## Corrección y límites

Los tres productores y consumidores usan un nombre estable por `github.run_id`
y, para los nativos, por módulo. Una repetición del productor sustituye su
artefacto completo mediante `overwrite: true`; un productor que ya pasó conserva
el suyo. No se mezclan ejecuciones ni se buscan coincidencias en otras ramas.

Se conservan las dependencias de los trabajos, la publicación de cobertura solo
después de pruebas satisfactorias y la comprobación de commit, árbol, módulo,
versión de coverage y hash de `.coveragerc` antes de combinar las mediciones.
Los artefactos de evidencia nativa, los resultados combinados y los diagnósticos
siguen identificados por intento. No se modifican reglas, umbrales, exclusiones
de Sonar, dependencias ni lógica clínica.

La regresión carga ambos YAML reales y recorre la entrega inicial y los reintentos
parciales, incluida la reutilización de productores anteriores y la sustitución
de los que vuelven a ejecutarse. Esta simulación verifica el contrato de nombres;
la comprobación del servicio real corresponde a los checks de la PR y su rama.
El resultado remoto se debe consultar en el commit exacto publicado, sin atribuir
un PASS nuevo al intento histórico fallido.

Verificación local observada: cuatro casos de entrega y cinco regresiones de
integración PASS; `git diff --check` PASS. Antes del arreglo, los casos de
reintento T05 y portable reprodujeron la ausencia del artefacto del consumidor.
Una revisión independiente del delta confirmó la conservación de los controles
de identidad, de éxito de los productores y del quality gate.

## Fuentes del comportamiento de Actions

- [Re-running workflows and jobs](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs):
  se conserva SHA/ref y los trabajos no repetidos mantienen sus resultados.
- [upload-artifact v4.6.2](https://github.com/actions/upload-artifact/blob/ea165f8d65b6e75b540449e92b4886f43607fa02/README.md):
  parámetro `overwrite`; sustitución completa de un artefacto del mismo nombre.
- [download-artifact v4](https://github.com/actions/download-artifact/blob/d3f86a106a0bac45b974a628896c90dbdf5c8093/README.md):
  la descarga por nombre se limita de forma predeterminada al workflow actual.

Estado clínico conservado: **CLINICALLY_PENDING**, sin GO_RELEASE.

## Comprobación real posterior de PR49

Commit publicado `318364bacf00cef22932f1849c79d12eb1e99562`, árbol
`b49ea28981e84f234a90aa2095ac5bbebb4ef92d`, idéntico al árbol probado localmente.
El run de PR [44798889446](https://github.com/JuanCopado/Emergency/actions/runs/44798889446)
pasó inicialmente. Se solicitó después la repetición exclusiva de Sonar,
sin volver a producir cobertura.

El [job del intento 2, 136511548666](https://github.com/JuanCopado/Emergency/actions/runs/44798889446/job/136511548666)
descargó los tres artefactos originales del intento 1:

| Productor | Artefacto | ID observado en API y log de descarga |
|---|---|---:|
| Portable | `test-coverage-44798889446` | 14661345310 |
| T05 Windows | `native-python-coverage-t05-44798889446` | 14659469020 |
| T06 Linux | `native-python-coverage-t06-44798889446` | 14659203571 |

Las tres descargas, la verificación de identidad y la combinación terminaron
correctamente. El escáner leyó `coverage.xml` y `app/coverage/lcov.info` y
registró **QUALITY GATE STATUS: PASSED** el 20/11/2026 a las **19:18:56Z**
(18:18:56 Atlantic/Azores). El nuevo artefacto combinado identifica el intento
2: `combined-test-coverage-44798889446-2`, ID `14661032054`.

El resultado prueba la recuperación real de mediciones de un intento anterior
por un consumidor reejecutado. No es solo una simulación ni un escáner omitido.
El intento histórico de PR48 permanece documentado como fallido antes del scan.
Los gates y sus umbrales no se han relajado. La conclusión de un workflow
independiente de push se registra aparte cuando finaliza.


## Cierre de rama e integración

El run de push [44798851854](https://github.com/JuanCopado/Emergency/actions/runs/44798851854)
terminó PASS en el intento 2. El primero consumió 15 min 44 s descargando
FFmpeg y agotó el límite de 20 minutos durante las pruebas. Se repitió solo
el productor portable; T05/T06 conservaron sus mediciones previas. El
[job Sonar 136519540092](https://github.com/JuanCopado/Emergency/actions/runs/44798851854/job/136519540092)
completó las tres descargas, comprobación de identidad, combinación, scan y
quality gate, todos PASS. No se aumentó el timeout ni se eludieron pruebas.

[PR49](https://github.com/JuanCopado/Emergency/pull/49) quedó integrada en
`f45b6286fa97ddb03be57005c5a90f916e9042e5`, árbol
`b49ea28981e84f234a90aa2095ac5bbebb4ef92d`, idéntico al comprobado. Se verificó
la identidad del merge; main/RC1/v1.43 permanecen fuera del destino.
