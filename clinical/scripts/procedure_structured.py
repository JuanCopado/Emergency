"""Deterministic, source-only procedure migration. No clinical text generation."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/procedures'
REVIEW = ROOT / 'references/procedure-safety-extractions-v1.42.json'
HEADER = re.compile(r'^## (PROC-[A-Z]+-\d{3}) — (.+?) — ([A-Z/]+)\s*$', re.M)
LABEL = re.compile(r'^\*\*([^\n*]+?):\*\*\s*', re.M)
FIELDS = {'Objetivo': 'objective', 'Indicaciones': 'indications',
          'Contraindicaciones/precauciones': 'contraindications_precautions',
          'Material': 'equipment', 'Anatomía': 'anatomy', 'Preparación': 'preparation',
          'Técnica paso a paso': 'steps', 'STOP': 'stop_points', 'Confirmación': 'confirmation',
          'Complicaciones': 'complications', 'Después': 'aftercare',
          'Documentación': 'documentation', 'Fuentes': 'sources', 'QA': 'qa',
          'Rescate': 'rescue', 'Escalada': 'escalation'}
ALIASES = {'PROC-ENT-011': 'PROC-ORTHO-022', 'PROC-PED-008': 'PROC-ORTHO-004',
           'PROC-SP-006': 'PROC-EYE-001', 'PROC-US-007': 'PROC-CV-006'}


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    def constant(value):
        raise ValueError(f'nonfinite JSON value: {value}')
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs,
                      parse_constant=constant)


def serialize(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n'


def canonical(root=ROOT):
    entries = {}
    family = None
    for line in (root / 'modules/emergency-procedures-index.md').read_text(encoding='utf-8').splitlines():
        group = re.match(r'^# \d+\. (.+)$', line)
        if group:
            family = group[1].strip()
        row = re.match(r'^\d+\. \*\*(PROC-[A-Z]+-\d{3}) — (.+?)\*\* — (.+?)\s*$', line)
        if not row:
            continue
        pid, name, level = row.groups()
        if pid in entries or not family:
            raise ValueError(f'duplicate/unscoped index ID: {pid}')
        alias = re.fullmatch(r'referencia cruzada a (?:PROC-)?([A-Z]+-\d{3})', level)
        entries[pid] = {'procedure_id': pid, 'name': name, 'family': family,
                        'level': None if alias else level,
                        'target': 'PROC-' + alias[1] if alias else None}
    cards = {}
    for path in sorted((root / 'modules/procedures').glob('*.md')):
        text = path.read_text(encoding='utf-8')
        headings = list(HEADER.finditer(text))
        for i, heading in enumerate(headings):
            pid, name, level = heading.groups()
            if pid in cards or pid not in entries:
                raise ValueError(f'duplicate/orphan card: {pid}')
            body = text[heading.end():headings[i+1].start() if i+1 < len(headings) else len(text)].strip()
            entry = entries[pid]
            if entry['target']:
                target = re.match(r'Ver \*\*(PROC-[A-Z]+-\d{3})\*\*', body)
                if level != 'REFERENCIA' or not target or target[1] != entry['target']:
                    raise ValueError(f'alias mismatch: {pid}')
                cards[pid] = {**entry, 'body': body}
                continue
            matches = list(LABEL.finditer(body))
            sections = {}
            for j, match in enumerate(matches):
                label = match[1]
                if label not in FIELDS or label in sections:
                    raise ValueError(f'unknown/duplicate section: {pid}: {label}')
                value = body[match.end():matches[j+1].start() if j+1 < len(matches) else len(body)].strip()
                if not value:
                    raise ValueError(f'empty section: {pid}: {label}')
                sections[label] = value
            if set(FIELDS) - {'Rescate', 'Escalada'} - sections.keys():
                raise ValueError(f'incomplete canonical card: {pid}')
            if not sections['QA'].startswith('YELLOW'):
                raise ValueError(f'clinical promotion requires human review: {pid}')
            cards[pid] = {**entry, 'card_name': name, 'card_level': level, 'sections': sections, 'body': body,
                         'source_path': path.relative_to(root).as_posix(),
                         'source_heading': heading[0].strip()[3:],
                         'family_preamble': text[:headings[0].start()].strip()}
    if set(cards) != set(entries):
        raise ValueError('index/card coverage mismatch')
    aliases = {pid: e['target'] for pid, e in entries.items() if e['target']}
    if aliases != ALIASES or any(target not in entries or entries[target]['target'] for target in aliases.values()):
        raise ValueError('broken/chained/unexpected aliases')
    return {pid: cards[pid] for pid in sorted(cards) if not cards[pid]['target']}, aliases


def project(card, reviews=None):
    sections = card['sections']
    result = {key: card[key] for key in ('procedure_id', 'name', 'family', 'level')}
    result.update(schema_version='1.42', status='YELLOW')
    for label, field in FIELDS.items():
        if field in ('rescue', 'escalation', 'qa'):
            continue
        value = sections[label]
        if field == 'objective':
            result[field] = value
        elif field in ('contraindications_precautions', 'equipment', 'anatomy', 'preparation', 'complications'):
            # The source does not classify these paragraphs into subcategories.
            result[field] = {'unclassified': [value]}
        elif field == 'steps':
            numbered = list(re.finditer(r'(?:^|;\s+)(\d+)\)\s+', value))
            if numbered and numbered[0].start() == 0:
                if [int(m[1]) for m in numbered] != list(range(1, len(numbered)+1)):
                    raise ValueError(f'noncontiguous source steps: {card["procedure_id"]}')
                result[field] = [{'order': i+1, 'action': value[m.end():numbered[i+1].start() if i+1 < len(numbered) else len(value)].strip()}
                                 for i, m in enumerate(numbered)]
            else:
                result[field] = [{'order': 1, 'action': value}]
        elif field == 'sources':
            result[field] = [{'title': value, 'organization': None, 'year': None}]
        else:
            result[field] = [value]
    safety = {}
    reviewed = (reviews or {}).get(card['procedure_id'], {})
    for field, label in (('rescue', 'Rescate'), ('escalation', 'Escalada')):
        excerpts = ([{'section': label, 'quote': sections[label]}] if label in sections else [])
        excerpts += reviewed.get(field, [])
        for excerpt in excerpts:
            if not excerpt['quote'].strip() or excerpt['quote'] not in sections.get(excerpt['section'], ''):
                raise ValueError(f'unsupported {field}: {card["procedure_id"]}')
        result[field] = [e['quote'] for e in excerpts] or None
        safety[field] = excerpts
    result['qa'] = {'clinical_qa': 'pending', 'visual_qa': 'paused', 'human_review_required': True,
                    'last_updated': None, 'notes': [sections['QA']]}
    result['aliases'] = sorted(pid for pid, target in ALIASES.items() if target == card['procedure_id'])
    result['provenance'] = {key: card[key] for key in ('source_path', 'source_heading', 'family_preamble')}
    result['provenance'].update(source_sha256=hashlib.sha256(card['body'].encode('utf-8')).hexdigest(),
                                sections=sections, safety_excerpts=safety)
    result['pending_review'] = [field for field in ('rescue', 'escalation') if result[field] is None]
    return result


def validate(data, schema=None):
    from jsonschema import Draft202012Validator
    schema = schema or load(ROOT / 'schemas/procedure-v1.42.schema.json')
    errors = [f'{e.json_path}: {e.message}' for e in Draft202012Validator(schema).iter_errors(data)]
    def inspect(value, path='$'):
        if isinstance(value, float) and not math.isfinite(value):
            errors.append(f'{path}: nonfinite')
        elif isinstance(value, list):
            signatures = [json.dumps(v, sort_keys=True, ensure_ascii=False) for v in value]
            if len(signatures) != len(set(signatures)):
                errors.append(f'{path}: duplicate list entries')
            for i, child in enumerate(value): inspect(child, f'{path}[{i}]')
        elif isinstance(value, dict):
            for key, child in value.items(): inspect(child, f'{path}.{key}')
    inspect(data)
    if isinstance(data.get('steps'), list):
        if [s.get('order') for s in data['steps'] if isinstance(s, dict)] != list(range(1, len(data['steps'])+1)):
            errors.append('steps: order is not contiguous')
    for field in ('rescue', 'escalation'):
        if (data.get(field) is None) != (field in data.get('pending_review', [])):
            errors.append(f'{field}: missing pending marker')
    return errors


def generate(family=None, check=False):
    cards, aliases = canonical()
    reviews = load(REVIEW)
    if set(reviews) - set(cards):
        raise ValueError('orphan safety extraction')
    selected = [c for c in cards.values() if family is None or c['procedure_id'].split('-')[1] == family]
    if not selected:
        raise ValueError(f'unknown family: {family}')
    outputs = []
    for card in selected:
        result = project(card, reviews)
        errors = validate(result)
        if errors:
            raise ValueError(f'{card["procedure_id"]}: {errors}')
        outputs.append((DATA / (card['procedure_id'] + '.json'), serialize(result)))
    # Validate the entire selected family before writing any file.
    for path, content in outputs:
        if check:
            if not path.exists() or path.read_text(encoding='utf-8') != content:
                raise ValueError(f'stale/missing artifact: {path.name}')
        else:
            path.write_text(content, encoding='utf-8', newline='\n')
    return len(outputs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    print(f'{generate(args.family, args.check)} procedures: PASS')
