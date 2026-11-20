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
