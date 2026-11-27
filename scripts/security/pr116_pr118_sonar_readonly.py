"""Fixed-project, read-only reliability and duplication metadata; no source or token output."""
import json
import os
import ssl
from urllib.request import HTTPSHandler, ProxyHandler, build_opener
import sonar_diagnostics as reader


def main():
    progress = {}
    try:
        selected = reader.selector(os.environ)
        token = os.environ['SONAR_TOKEN']
        context = ssl.create_default_context()
        opener = build_opener(ProxyHandler({}), HTTPSHandler(context=context), reader.NoRedirects())
        # This isolated diagnostic branch adds only these two metadata GET paths.
        reader.ENDPOINTS = reader.ENDPOINTS | {'/api/measures/component_tree', '/api/duplications/show'}
        def get(path, parameters):
            return reader.request_json(opener, path, {**parameters, **selected}, token, progress)
        gate = get('/api/qualitygates/project_status', {'projectKey': reader.PROJECT})
        data = get('/api/issues/search', {'organization': reader.ORGANIZATION,
            'componentKeys': reader.PROJECT, 'resolved': 'false', 'ps': '100', 'p': '1'})
        issues = [reader.public_fields(item, reader.ISSUE_FIELDS + ('type',), token) for item in data['issues']]
        files = get('/api/measures/component_tree', {'component': reader.PROJECT,
            'metricKeys': 'new_duplicated_lines_density,new_duplicated_lines', 'qualifiers': 'FIL', 'strategy': 'all', 'ps': '500', 'p': '1'})
        duplicated = []
        for item in files.get('components', []):
            key = item.get('key', '')
            if not key.startswith(reader.PROJECT + ':'):
                raise ValueError('Unexpected project')
            metrics = item.get('measures', [])
            values = [value for m in metrics for value in [m.get('value', '0'), m.get('period', {}).get('value', '0'), *[p.get('value', '0') for p in m.get('periods', [])]]]
            if not any(float(value) > 0 for value in values):
                continue
            blocks = get('/api/duplications/show', {'key': key})
            duplicated.append({'component': key, 'measures': metrics,
                'duplications': blocks.get('duplications', []),
                'files': {ref: {'key': f.get('key'), 'name': f.get('name')} for ref, f in blocks.get('files', {}).items()}})
        result = {'subject': selected, 'conditions': [reader.public_fields(c, reader.CONDITION_FIELDS, token)
            for c in gate['projectStatus']['conditions']], 'issue_total': data.get('total', data.get('paging', {}).get('total')),
            'issues': issues, 'duplication_components': duplicated}
        encoded = json.dumps(result, ensure_ascii=True)
        if token in encoded:
            raise ValueError('Unsafe output')
        print(encoded)
        return 0
    except Exception:
        print(json.dumps({'diagnostic_status': 'UNAVAILABLE', 'progress': progress}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
