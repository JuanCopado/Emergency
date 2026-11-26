# Protobuf UTF-8 de Sonar · reproducción y corrección acotada

La investigación del 26/11/2026 usa el tag exacto SonarJS 14.6.0.46571, commit `b5adf957c1f021ed3ceb78f04be9c7b701a86945`, observado en los logs del receptor y de PR114.

Fuentes primarias verificadas:

- [Serializador visitLiteral, ast.ts](https://github.com/SonarSource/SonarJS/blob/b5adf957c1f021ed3ceb78f04be9c7b701a86945/packages/analysis/src/jsts/parsers/ast.ts#L520): copia el valor de un literal string a `valueString`.
- [Esquema estree.proto](https://github.com/SonarSource/SonarJS/blob/b5adf957c1f021ed3ceb78f04be9c7b701a86945/packages/analysis/src/jsts/parsers/estree.proto#L231).
- [AstProtoUtils](https://github.com/SonarSource/SonarJS/blob/b5adf957c1f021ed3ceb78f04be9c7b701a86945/sonar-plugin/bridge/src/main/java/org/sonar/plugins/javascript/bridge/AstProtoUtils.java#L53): ante InvalidProtocolBufferException registra el error y devuelve null.
- [WebSensor](https://github.com/SonarSource/SonarJS/blob/b5adf957c1f021ed3ceb78f04be9c7b701a86945/sonar-plugin/sonar-javascript-plugin/src/main/java/org/sonar/plugins/javascript/analysis/WebSensor.java#L742): no invoca los consumidores AST si el resultado es null. El contador de archivos no acredita esa entrega.

## Reproducción sin cambiar el producto

El script de custodia `SONAR_INVESTIGACION/reproduce_sonar_ast.py` usa el AST real de `app/src/t06/viewModel.test.ts`, el serializador y esquema publicados del tag exacto y protobufjs 8.8.1 con integridad SHA-512 de npm comprobada. La reproducción detecta dos strings UTF-16 no bien formados en `literal.valueString`: los controles surrogate aislados D800 y DFFF. Writer.string produce `03 ed a0 80` y `03 ed bf bf`, inválidos en UTF-8 estricto.

Antes: dos strings AST no bien formados, Protobuf de 51.866 bytes. Sustitución solo en memoria por `String.fromCharCode(0xd800)` / `String.fromCharCode(0xdfff)`: mismos dos controles en ejecución, cero strings AST no bien formados, Protobuf de 52.084 bytes. Script, hashes de fuentes, comando y resultados se conservan en la custodia Windows del supercoordinador.

El parche aplica esas dos sustituciones exclusivamente al test y explica el motivo. No elimina casos, cambia el filtro, reglas, exclusiones, umbrales o datos clínicos. Suite focal T06/viewModel y conexión de nota: 138 PASS; lint PASS.

## Criterio de verificación pendiente

La reproducción demuestra el mecanismo y corrige esa entrada concreta del serializador. Los logs anteriores no identifican su payload fallido, por lo que no se atribuye retrospectivamente ese error a un archivo con certeza. Debe ejecutarse CI y Sonar sobre el SHA publicado con el parche y comprobar si desaparece el diagnóstico. Su ausencia permitirá registrar que no se reproduce en esa ejecución, no certificar exhaustivamente todos los consumidores AST o validez clínica.

Auditoría independiente del mismo candidato y CI completa siguen siendo condiciones de integración. CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.

## Conciliación de procedencia T06

La primera CI con la sustitución falló realmente: la guarda T06 esperaba el hash del test Q4 original entre19 archivos recuperados. No se registra ese intento como PASS. Se mantiene `SOURCE_PROVENANCE.json` intacto y se añade una adaptación vigente explícita en `CURRENT_ADAPTATIONS.json`, con original congelado y hashes anterior/nuevo. El verificador exige18 destinos idénticos y la transformación exacta del destino19, conservando sus bytes originales en custodia. Tres pruebas puras adicionales detectan retirada de aserción, alteración del original o reetiquetado de hash. No se cambian los dos adaptadores históricos ni el transporte R6/B1. La prueba Linux completa se vuelve a ejecutar sobre el SHA publicado con esta conciliación.
