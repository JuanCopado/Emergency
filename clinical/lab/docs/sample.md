# Muestra de composición (prueba del generador)

Esta muestra ejercita el generador con tablas anchas, una tabla larga que cruza páginas y fórmulas. Sin contenido clínico.

## Fórmulas

Cota superior a una cara para cero eventos en $P$ participantes: $u_{\text{part}} = 1 - 0.05^{1/P} \approx \frac{3}{P}$, y a dos caras $1 - 0.025^{1/P}$.

$$\widehat{\text{DEFF}} = 1 + (\bar{m}-1)\hat{\rho}, \qquad \hat{\Delta}_{\text{ensayo}} = \hat{p}_{\text{ensayo},B} - \hat{p}_{\text{ensayo},A}$$

$$\hat{q}_{\text{part},k} = \frac{1}{P}\sum_{i=1}^{P}\mathbb{I}(Y_{i,k} \ge 1)$$

La regla de BCa exige $P \ge 20$, al menos 2 participantes con eventos y 2 sin eventos; si no, `FALLBACK_SMALL_SAMPLE_OR_DEGENERATE`. Dimensión: 360 $\times$ 640 px; pérdida 0\% de bloqueos.

## Tabla ancha de siete columnas

| Par | Mec. | Escenario | Destino | Especificación Set 1 | Especificación Set 2 | Control de dificultad y respuesta esperada |
|---|---|---|---|---|---|---|
| 01 | M3 | A (válido) | Piel/Heridas | Herida superficial abierta sin cierre visible; piel clara, luz neutra, JPEG RGB. | Herida superficial abierta sin cierre visible; piel clara, luz neutra, JPEG RGB. | Baja-media; control cutáneo y cláusula R14-01. |
| 04 | M1 | B (error) | Ruta ECG | Galería de 4 miniaturas contiguas (IMG_4102.jpg–4105.jpg): herida sintética sobre fondo claro junto a ECG. | Galería de 4 miniaturas contiguas (IMG_5201.jpg–5204.jpg): herida sintética sobre gasa. | Error deliberado en galería; la capa 7 no dispara (JPEG válido). |
| 15 | M2 | E2 (capa 7) | Corrupto / incompatible | Corrupción técnica (T7-03): JPEG truncado en ruta fotográfica. | Incompatibilidad (T7-04): PDF textual sintético enviado a ruta exclusivamente fotográfica. | Disparo esperado en el brazo B; excluido de B frente a A. |

## Tabla larga con encabezado repetido

| Id | Concepto | Valor | Nota |
|---|---|---|---|
| 001 | Fila de prueba número 1 con texto suficiente para ocupar una línea completa de la tabla | 3 | nota 1 |
| 002 | Fila de prueba número 2 con texto suficiente para ocupar una línea completa de la tabla | 6 | nota 2 |
| 003 | Fila de prueba número 3 con texto suficiente para ocupar una línea completa de la tabla | 9 | nota 3 |
| 004 | Fila de prueba número 4 con texto suficiente para ocupar una línea completa de la tabla | 12 | nota 4 |
| 005 | Fila de prueba número 5 con texto suficiente para ocupar una línea completa de la tabla | 15 | nota 5 |
| 006 | Fila de prueba número 6 con texto suficiente para ocupar una línea completa de la tabla | 18 | nota 6 |
| 007 | Fila de prueba número 7 con texto suficiente para ocupar una línea completa de la tabla | 21 | nota 0 |
| 008 | Fila de prueba número 8 con texto suficiente para ocupar una línea completa de la tabla | 24 | nota 1 |
| 009 | Fila de prueba número 9 con texto suficiente para ocupar una línea completa de la tabla | 27 | nota 2 |
| 010 | Fila de prueba número 10 con texto suficiente para ocupar una línea completa de la tabla | 30 | nota 3 |
| 011 | Fila de prueba número 11 con texto suficiente para ocupar una línea completa de la tabla | 33 | nota 4 |
| 012 | Fila de prueba número 12 con texto suficiente para ocupar una línea completa de la tabla | 36 | nota 5 |
| 013 | Fila de prueba número 13 con texto suficiente para ocupar una línea completa de la tabla | 39 | nota 6 |
| 014 | Fila de prueba número 14 con texto suficiente para ocupar una línea completa de la tabla | 42 | nota 0 |
| 015 | Fila de prueba número 15 con texto suficiente para ocupar una línea completa de la tabla | 45 | nota 1 |
| 016 | Fila de prueba número 16 con texto suficiente para ocupar una línea completa de la tabla | 48 | nota 2 |
| 017 | Fila de prueba número 17 con texto suficiente para ocupar una línea completa de la tabla | 51 | nota 3 |
| 018 | Fila de prueba número 18 con texto suficiente para ocupar una línea completa de la tabla | 54 | nota 4 |
| 019 | Fila de prueba número 19 con texto suficiente para ocupar una línea completa de la tabla | 57 | nota 5 |
| 020 | Fila de prueba número 20 con texto suficiente para ocupar una línea completa de la tabla | 60 | nota 6 |
| 021 | Fila de prueba número 21 con texto suficiente para ocupar una línea completa de la tabla | 63 | nota 0 |
| 022 | Fila de prueba número 22 con texto suficiente para ocupar una línea completa de la tabla | 66 | nota 1 |
| 023 | Fila de prueba número 23 con texto suficiente para ocupar una línea completa de la tabla | 69 | nota 2 |
| 024 | Fila de prueba número 24 con texto suficiente para ocupar una línea completa de la tabla | 72 | nota 3 |
| 025 | Fila de prueba número 25 con texto suficiente para ocupar una línea completa de la tabla | 75 | nota 4 |
| 026 | Fila de prueba número 26 con texto suficiente para ocupar una línea completa de la tabla | 78 | nota 5 |
| 027 | Fila de prueba número 27 con texto suficiente para ocupar una línea completa de la tabla | 81 | nota 6 |
| 028 | Fila de prueba número 28 con texto suficiente para ocupar una línea completa de la tabla | 84 | nota 0 |
| 029 | Fila de prueba número 29 con texto suficiente para ocupar una línea completa de la tabla | 87 | nota 1 |
| 030 | Fila de prueba número 30 con texto suficiente para ocupar una línea completa de la tabla | 90 | nota 2 |
| 031 | Fila de prueba número 31 con texto suficiente para ocupar una línea completa de la tabla | 93 | nota 3 |
| 032 | Fila de prueba número 32 con texto suficiente para ocupar una línea completa de la tabla | 96 | nota 4 |
| 033 | Fila de prueba número 33 con texto suficiente para ocupar una línea completa de la tabla | 99 | nota 5 |
| 034 | Fila de prueba número 34 con texto suficiente para ocupar una línea completa de la tabla | 102 | nota 6 |
| 035 | Fila de prueba número 35 con texto suficiente para ocupar una línea completa de la tabla | 105 | nota 0 |
| 036 | Fila de prueba número 36 con texto suficiente para ocupar una línea completa de la tabla | 108 | nota 1 |
| 037 | Fila de prueba número 37 con texto suficiente para ocupar una línea completa de la tabla | 111 | nota 2 |
| 038 | Fila de prueba número 38 con texto suficiente para ocupar una línea completa de la tabla | 114 | nota 3 |
| 039 | Fila de prueba número 39 con texto suficiente para ocupar una línea completa de la tabla | 117 | nota 4 |
| 040 | Fila de prueba número 40 con texto suficiente para ocupar una línea completa de la tabla | 120 | nota 5 |
| 041 | Fila de prueba número 41 con texto suficiente para ocupar una línea completa de la tabla | 123 | nota 6 |
| 042 | Fila de prueba número 42 con texto suficiente para ocupar una línea completa de la tabla | 126 | nota 0 |
| 043 | Fila de prueba número 43 con texto suficiente para ocupar una línea completa de la tabla | 129 | nota 1 |
| 044 | Fila de prueba número 44 con texto suficiente para ocupar una línea completa de la tabla | 132 | nota 2 |
| 045 | Fila de prueba número 45 con texto suficiente para ocupar una línea completa de la tabla | 135 | nota 3 |
| 046 | Fila de prueba número 46 con texto suficiente para ocupar una línea completa de la tabla | 138 | nota 4 |
| 047 | Fila de prueba número 47 con texto suficiente para ocupar una línea completa de la tabla | 141 | nota 5 |
| 048 | Fila de prueba número 48 con texto suficiente para ocupar una línea completa de la tabla | 144 | nota 6 |
| 049 | Fila de prueba número 49 con texto suficiente para ocupar una línea completa de la tabla | 147 | nota 0 |
| 050 | Fila de prueba número 50 con texto suficiente para ocupar una línea completa de la tabla | 150 | nota 1 |
| 051 | Fila de prueba número 51 con texto suficiente para ocupar una línea completa de la tabla | 153 | nota 2 |
| 052 | Fila de prueba número 52 con texto suficiente para ocupar una línea completa de la tabla | 156 | nota 3 |
| 053 | Fila de prueba número 53 con texto suficiente para ocupar una línea completa de la tabla | 159 | nota 4 |
| 054 | Fila de prueba número 54 con texto suficiente para ocupar una línea completa de la tabla | 162 | nota 5 |
| 055 | Fila de prueba número 55 con texto suficiente para ocupar una línea completa de la tabla | 165 | nota 6 |
| 056 | Fila de prueba número 56 con texto suficiente para ocupar una línea completa de la tabla | 168 | nota 0 |
| 057 | Fila de prueba número 57 con texto suficiente para ocupar una línea completa de la tabla | 171 | nota 1 |
| 058 | Fila de prueba número 58 con texto suficiente para ocupar una línea completa de la tabla | 174 | nota 2 |
| 059 | Fila de prueba número 59 con texto suficiente para ocupar una línea completa de la tabla | 177 | nota 3 |
| 060 | Fila de prueba número 60 con texto suficiente para ocupar una línea completa de la tabla | 180 | nota 4 |
| 061 | Fila de prueba número 61 con texto suficiente para ocupar una línea completa de la tabla | 183 | nota 5 |
| 062 | Fila de prueba número 62 con texto suficiente para ocupar una línea completa de la tabla | 186 | nota 6 |
| 063 | Fila de prueba número 63 con texto suficiente para ocupar una línea completa de la tabla | 189 | nota 0 |
| 064 | Fila de prueba número 64 con texto suficiente para ocupar una línea completa de la tabla | 192 | nota 1 |
| 065 | Fila de prueba número 65 con texto suficiente para ocupar una línea completa de la tabla | 195 | nota 2 |
| 066 | Fila de prueba número 66 con texto suficiente para ocupar una línea completa de la tabla | 198 | nota 3 |
| 067 | Fila de prueba número 67 con texto suficiente para ocupar una línea completa de la tabla | 201 | nota 4 |
| 068 | Fila de prueba número 68 con texto suficiente para ocupar una línea completa de la tabla | 204 | nota 5 |
| 069 | Fila de prueba número 69 con texto suficiente para ocupar una línea completa de la tabla | 207 | nota 6 |
| 070 | Fila de prueba número 70 con texto suficiente para ocupar una línea completa de la tabla | 210 | nota 0 |
| 071 | Fila de prueba número 71 con texto suficiente para ocupar una línea completa de la tabla | 213 | nota 1 |
| 072 | Fila de prueba número 72 con texto suficiente para ocupar una línea completa de la tabla | 216 | nota 2 |
| 073 | Fila de prueba número 73 con texto suficiente para ocupar una línea completa de la tabla | 219 | nota 3 |
| 074 | Fila de prueba número 74 con texto suficiente para ocupar una línea completa de la tabla | 222 | nota 4 |
| 075 | Fila de prueba número 75 con texto suficiente para ocupar una línea completa de la tabla | 225 | nota 5 |
| 076 | Fila de prueba número 76 con texto suficiente para ocupar una línea completa de la tabla | 228 | nota 6 |
| 077 | Fila de prueba número 77 con texto suficiente para ocupar una línea completa de la tabla | 231 | nota 0 |
| 078 | Fila de prueba número 78 con texto suficiente para ocupar una línea completa de la tabla | 234 | nota 1 |
| 079 | Fila de prueba número 79 con texto suficiente para ocupar una línea completa de la tabla | 237 | nota 2 |
| 080 | Fila de prueba número 80 con texto suficiente para ocupar una línea completa de la tabla | 240 | nota 3 |
| 081 | Fila de prueba número 81 con texto suficiente para ocupar una línea completa de la tabla | 243 | nota 4 |
| 082 | Fila de prueba número 82 con texto suficiente para ocupar una línea completa de la tabla | 246 | nota 5 |
| 083 | Fila de prueba número 83 con texto suficiente para ocupar una línea completa de la tabla | 249 | nota 6 |
| 084 | Fila de prueba número 84 con texto suficiente para ocupar una línea completa de la tabla | 252 | nota 0 |
| 085 | Fila de prueba número 85 con texto suficiente para ocupar una línea completa de la tabla | 255 | nota 1 |
| 086 | Fila de prueba número 86 con texto suficiente para ocupar una línea completa de la tabla | 258 | nota 2 |
| 087 | Fila de prueba número 87 con texto suficiente para ocupar una línea completa de la tabla | 261 | nota 3 |
| 088 | Fila de prueba número 88 con texto suficiente para ocupar una línea completa de la tabla | 264 | nota 4 |
| 089 | Fila de prueba número 89 con texto suficiente para ocupar una línea completa de la tabla | 267 | nota 5 |
| 090 | Fila de prueba número 90 con texto suficiente para ocupar una línea completa de la tabla | 270 | nota 6 |
| 091 | Fila de prueba número 91 con texto suficiente para ocupar una línea completa de la tabla | 273 | nota 0 |
| 092 | Fila de prueba número 92 con texto suficiente para ocupar una línea completa de la tabla | 276 | nota 1 |
| 093 | Fila de prueba número 93 con texto suficiente para ocupar una línea completa de la tabla | 279 | nota 2 |
| 094 | Fila de prueba número 94 con texto suficiente para ocupar una línea completa de la tabla | 282 | nota 3 |
| 095 | Fila de prueba número 95 con texto suficiente para ocupar una línea completa de la tabla | 285 | nota 4 |
| 096 | Fila de prueba número 96 con texto suficiente para ocupar una línea completa de la tabla | 288 | nota 5 |
| 097 | Fila de prueba número 97 con texto suficiente para ocupar una línea completa de la tabla | 291 | nota 6 |
| 098 | Fila de prueba número 98 con texto suficiente para ocupar una línea completa de la tabla | 294 | nota 0 |
| 099 | Fila de prueba número 99 con texto suficiente para ocupar una línea completa de la tabla | 297 | nota 1 |
| 100 | Fila de prueba número 100 con texto suficiente para ocupar una línea completa de la tabla | 300 | nota 2 |
| 101 | Fila de prueba número 101 con texto suficiente para ocupar una línea completa de la tabla | 303 | nota 3 |
| 102 | Fila de prueba número 102 con texto suficiente para ocupar una línea completa de la tabla | 306 | nota 4 |
| 103 | Fila de prueba número 103 con texto suficiente para ocupar una línea completa de la tabla | 309 | nota 5 |
| 104 | Fila de prueba número 104 con texto suficiente para ocupar una línea completa de la tabla | 312 | nota 6 |
| 105 | Fila de prueba número 105 con texto suficiente para ocupar una línea completa de la tabla | 315 | nota 0 |
| 106 | Fila de prueba número 106 con texto suficiente para ocupar una línea completa de la tabla | 318 | nota 1 |
| 107 | Fila de prueba número 107 con texto suficiente para ocupar una línea completa de la tabla | 321 | nota 2 |
| 108 | Fila de prueba número 108 con texto suficiente para ocupar una línea completa de la tabla | 324 | nota 3 |
| 109 | Fila de prueba número 109 con texto suficiente para ocupar una línea completa de la tabla | 327 | nota 4 |
| 110 | Fila de prueba número 110 con texto suficiente para ocupar una línea completa de la tabla | 330 | nota 5 |
| 111 | Fila de prueba número 111 con texto suficiente para ocupar una línea completa de la tabla | 333 | nota 6 |
| 112 | Fila de prueba número 112 con texto suficiente para ocupar una línea completa de la tabla | 336 | nota 0 |
| 113 | Fila de prueba número 113 con texto suficiente para ocupar una línea completa de la tabla | 339 | nota 1 |
| 114 | Fila de prueba número 114 con texto suficiente para ocupar una línea completa de la tabla | 342 | nota 2 |
| 115 | Fila de prueba número 115 con texto suficiente para ocupar una línea completa de la tabla | 345 | nota 3 |
| 116 | Fila de prueba número 116 con texto suficiente para ocupar una línea completa de la tabla | 348 | nota 4 |
| 117 | Fila de prueba número 117 con texto suficiente para ocupar una línea completa de la tabla | 351 | nota 5 |
| 118 | Fila de prueba número 118 con texto suficiente para ocupar una línea completa de la tabla | 354 | nota 6 |
| 119 | Fila de prueba número 119 con texto suficiente para ocupar una línea completa de la tabla | 357 | nota 0 |
| 120 | Fila de prueba número 120 con texto suficiente para ocupar una línea completa de la tabla | 360 | nota 1 |
