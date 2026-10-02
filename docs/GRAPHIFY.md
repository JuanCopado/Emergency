# Graphify en Emergency

Graphify se usa como **índice/grafo auxiliar del repositorio**, no como fuente clínica ni como sustituto del registro de evidencia.

## Instalación recomendada
Requiere Python >=3.10.

```bash
uv tool install graphifyy
graphify install --project --platform codex
```

El paquete oficial en PyPI es `graphifyy`; el comando es `graphify`.

## Construcción
Desde la raíz del repositorio:

```bash
graphify .
```

En Codex, tras instalar la skill de proyecto, se puede invocar `$graphify`.

La salida habitual queda en `graphify-out/` y debe tratarse como artefacto generado localmente.

## Actualización incremental
Tras cambios del repositorio:

```bash
graphify update .
```

## Política de seguridad
- Excluir `node_modules/`, `dist/`, ZIPs, binarios generados y datos clínicos identificables.
- No usar relaciones inferidas por Graphify como evidencia clínica.
- Las relaciones clínicas normativas proceden exclusivamente de módulos revisados y del registro de evidencia.
- No versionar un grafo que contenga información sensible.

## Uso recomendado
- localizar dependencias entre documentación y código;
- detectar módulos huérfanos o documentación duplicada;
- encontrar puntos centrales del proyecto;
- reducir lecturas repetidas del repositorio;
- apoyar auditorías técnicas.

Para el grafo clínico determinista del proyecto usar además:
```bash
python3 clinical/scripts/build_project_graph.py
```
