# R43 · Comparación de regresiones Python

**CLINICALLY_PENDING · NO_GO_CLINICAL_RELEASE.**

El informe R41 publicado con el parche reporta 19 errores en Linux/Python 3.13 sin lista de tests. Conserva una traza `OSError: cannot open resource`. Ese informe no permite asociar sus 19 errores a nombres de casos concretos.

## Comparación de suites completas

Dos worktrees independientes en `dcc48b3cc115a7de5f45e9a2a89d06673ba8fe15`, el segundo con el parche original de 14 archivos aplicado mediante `git apply --index`. En ambos se ejecutó `python -m unittest discover -s clinical/tests -p 'test_*.py' -v` con el mismo Python 3.12.14, dependencias, modelo OCR verificado, módulos Node de OCR y `BG_TEST_FONT` apuntando a DejaVuSans del repositorio, como en CI.

| Ejecución | Pruebas | Omitidas | Fallos | Errores |
| --- | ---: | ---: | ---: | ---: |
| Base `dcc48b3` | 1615 | 16 | 0 | 0 |
| Base con parche original | 1624 | 16 | 0 | 0 |

El delta son nueve pruebas de pt-BR aprobadas. Los resultados individuales de las pruebas comunes coincidieron. En condiciones equivalentes con los recursos de CI no se demuestra ninguna regresión Python atribuible al parche.

## Control de la traza de fuente

Se repitieron exclusivamente los dos módulos que llaman a Pillow con `BG_TEST_FONT` y fallback `arial.ttf`, con el modelo OCR y los módulos Node iguales y la variable de fuente retirada. En ambos lados, 29 pruebas, 2 omitidas y las mismas 4 trazas `OSError: cannot open resource`:

- `test_blood_gas_multiformat.Validation.test_formats`.
- `test_blood_gas_multiformat.Validation.test_mixed_pdf_layers_warn`.
- `test_blood_gas_par01.SampleSegmentation.test_pdf_raster_specimen_and_conflicting_text_layer_retain_provenance`, para las subpruebas `native=''` y `native='Muestra: venosa'`.

La firma de error comunicada se reproduce como un problema de entorno preexistente. La correspondencia individual con los 19 errores de la sesión R41 queda indeterminada sin su registro completo. La suite de comparación permite descartar una diferencia entre base y parche en el entorno comprobado.

## Ajuste observable en la integración R43

El informe de Chromium puede registrar dos eventos `locale_resolved` idénticos durante un mismo ensayo. La regresión ahora exige como mínimo un evento, y que todos los eventos de resolución observados prueben el mismo estrato pt-BR, antes de validar cada uno de los ocho sellos. Se conserva la regresión independiente de los 24 sellos históricos introducida por PR99.
