#!/usr/bin/env python3
"""Reproducible offline R5 extension of R4-SCA-SILENT; synthetic data only.

Writes research artifacts outside the repository. Never changes product rules,
clinical state, scores, alerts or recommendations. No medical accuracy claim.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

BASE = '95c5f25f755e27628baf8e5f69f60df2b308ea92'
TREE = '8dae69dad71b0b917a2caa35b81a286e4bbf5c74'
ACS = 'acute-coronary-syndrome'
CONTROLS = [
    ('possible', 'Possible ST elevation. Nausea.', True),
    ('affirmed', 'ST elevation. Nausea.', False),
    ('no-st', 'Nausea.', False),
    ('denied', 'No ST elevation. Nausea.', False),
    ('history', 'History of ST elevation. Nausea.', False),
    ('family', 'Mother has ST elevation. Nausea.', False),
    ('only-possible', 'Possible ST elevation.', False),
    ('synonyms', 'Possible ST elevation. Possible STEMI. Nausea.', True),
    ('possible-denied', 'Possible ST elevation. No ST elevation. Nausea.', True),
    ('affirmed-denied', 'ST elevation. No ST elevation. Nausea.', False),
    ('remaining-sufficient', 'ST elevation. Chest pain. Possible nausea.', False),
    ('remaining-insufficient', 'ST elevation. Possible nausea.', True),
]
# These are test sentences, not additions to the clinical vocabulary. Missing
# language terms are deliberately retained and reported rather than translated
# into an already-supported term or assigned a new score.
TERMS = {
    ACS: {'es-ES': ('elevación del ST', 'Náusea'),
          'pt-PT': ('supradesnivelamento de ST', 'Náusea'),
          'en': ('ST elevation', 'Nausea')},
    'cardiac-tamponade-pericardial-emergency': {
        'es-ES': ('taponamiento cardíaco', 'Derrame pericárdico'),
        'pt-PT': ('tamponamento', 'Derrame pericárdico'),
        'en': ('tamponade', 'Pericardial effusion')},
    'infective-endocarditis': {
        'es-ES': ('endocarditis infecciosa', 'Hemocultivos positivos'),
        'pt-PT': ('endocardite infecciosa', 'Hemoculturas positivas'),
        'en': ('infective endocarditis', 'Positive blood cultures')},
}
PREFIXES = {
    'es-ES': ('Posible ', 'Sin ', 'Historia de ', 'Madre con '),
    'pt-PT': ('Possível ', 'Sem ', 'História de ', 'Mãe com '),
    'en': ('Possible ', 'No ', 'History of ', 'Mother has '),
}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                    separators=(',', ':')).encode()).hexdigest()


def shadow(result, high):
    hit = next((h for h in result['rule_hits'] if h['module'] == ACS), {})
    basis = hit.get('score_basis', {})
    eligible = hit.get('score', 0) >= high and basis.get('category_depends_on_unconfirmed') is True
    if eligible:
        assert basis['remaining_points'] < high <= hit['score']
        assert basis['remaining_points'] + basis['unconfirmed_points'] == hit['score']
    return {'review_priority_candidate_offline_only': eligible,
            'clinical_certainty': 'not established; medical review pending',
            'acs_score': hit.get('score', 0), 'acs_score_basis': basis}


def matrix():
    for module, languages in TERMS.items():
        for language, (term, companion) in languages.items():
            possible, denied, history, family = PREFIXES[language]
            texts = {
                'affirmed': term + '.', 'denied': denied + term + '.',
                'uncertain': possible + term + '.', 'historical': history + term + '.',
                'other-person': family + term + '.',
                'contradictory': term + '. ' + denied + term + '.',
                'uncertain-denied': possible + term + '. ' + denied + term + '.',
                'uncertain-with-companion': possible + term + '. ' + companion + '.',
            }
            for state, text in texts.items():
                yield f'{module}/{language}/{state}', module, language, state, text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--commit', default=BASE)
    parser.add_argument('--tree', default=TREE)
    args = parser.parse_args()
    def git(*argv):
        return subprocess.check_output(['git', '-C', str(args.repo), *argv])
    commit = git('rev-parse', args.commit + '^{commit}').decode().strip()
    tree = git('rev-parse', commit + '^{tree}').decode().strip()
    if tree != args.tree:
        raise SystemExit('Tree identity mismatch; no study executed')
    output = args.output.resolve()
    if output.is_relative_to(args.repo.resolve()):
        raise SystemExit('Output must be outside the candidate repository')
    if output.exists():
        raise SystemExit('Output already exists; choose a new artifact directory')
    with tempfile.TemporaryDirectory(prefix='emergency-r5-note-') as temporary:
        with zipfile.ZipFile(io.BytesIO(git('archive', '--format=zip', commit, 'clinical'))) as archive:
            archive.extractall(temporary)
        clinical = Path(temporary) / 'clinical'
        sys.path[:0] = [str(clinical/'scripts'), str(clinical/'tests')]
        from clinical_note_diagnostic_engine import analyze, load_rules, _norm, _term_states
        from run_clinical_note_diagnostic_cases import build
        from test_clinical_note_provenance import corpus
        rules = load_rules()
        high = rules['qualitative_confidence']['high']['minimum_score']
        ids = {r['id'] for r in rules['syndromes']}
        registered = set(json.loads((clinical/'references/evidence-registry.json').read_text(encoding='utf8'))['modules'])
        edges = [{'source': r['id'], 'target': target, 'registered_module': target in registered}
                 for r in rules['syndromes'] for target in r.get('must_not_miss', []) if target not in ids]
        frozen = list(corpus())
        assert len(frozen) == 60
        entries = [('frozen/'+i, n, None, None) for i, n in frozen]
        entries += [('r4-control/'+i, build({'age_years':40, 'hpi':text}), expected, None)
                    for i, text, expected in CONTROLS]
        entries += [(i, build({'age_years':40, 'hpi':text}), None,
                     {'module':m, 'language':lang, 'state':s, 'text':text}) for i,m,lang,s,text in matrix()]
        for edge in edges:
            source = next(r for r in rules['syndromes'] if r['id']==edge['source'])
            terms = [tr['terms'][0] for tr in source['triggers'] if tr.get('terms')]
            assert terms, edge
            age = 10 if source['id'].startswith('pediatric-') else 40
            entries.append(('unresolved-edge/'+source['id'],
                            build({'age_years':age, 'hpi':'. '.join(terms)+'.'}), None, None))
        records = []
        for case, note, expected, metadata in entries:
            note['encounter']['encounter_id'] = 'SYNTH-R5-' + case
            if metadata:
                note['language'] = metadata['language']
            before = analyze(note, apply_to_note=True)
            assert not before['blocked'], case
            if case.startswith('unresolved-edge/'):
                source = case.split('/',1)[1]
                edge = next(e for e in edges if e['source']==source)
                assert any(h['module']==source for h in before['rule_hits']), case
                assert any(edge['target'] in line for line in before['assessment']['limitations']), case
                assert not any(edge['target'] in d['source_modules'] for d in before['assessment']['must_not_miss']), case
            before_hash = digest(before)
            marker = shadow(before, high)
            assert before_hash == digest(before), case
            # Independent rerun, preserving the untouched input and full output.
            after = analyze(note, apply_to_note=True)
            assert before_hash == digest(after), case
            if expected is not None:
                assert marker['review_priority_candidate_offline_only'] is expected, case
            row = {'case':case, 'synthetic':True, 'metadata':metadata, 'input':note,
                   'before':before, 'after':after, 'before_sha256':before_hash,
                   'after_sha256':digest(after), 'shadow_observer':marker}
            if metadata:
                module = metadata['module']
                hit = next((h for h in before['rule_hits'] if h['module']==module), {})
                primary = TERMS[module][metadata['language']][0]
                row['target_observation'] = {'score':hit.get('score',0), 'basis':hit.get('score_basis'),
                    'primary_term_states':sorted(_term_states(primary, _norm(metadata['text']))),
                    'primary_term_in_catalogue':any(_norm(primary)==_norm(t) for r in rules['syndromes']
                        if r['id']==module for tr in r['triggers'] for t in tr.get('terms',[]))}
            records.append(row)
        output.mkdir(parents=True)
        report = {'study':'R4-SCA-SILENT-20261121-v1/R5-offline-extension',
                  'product_commit':commit,'product_tree':tree,'status':'CLINICALLY_PENDING',
                  'threshold_read_from_product':high,'synthetic_cases':len(records),'frozen_cases':len(frozen),
                  'r4_controls':len(CONTROLS), 'multilingual_minimal_pairs':72, 'unresolved_edge_probes':len(edges),
                  'outputs_unchanged':sum(r['before_sha256']==r['after_sha256'] for r in records),
                  'full_outputs_digest':digest([r['before_sha256'] for r in records]),
                  'unresolved_targets':sorted({e['target'] for e in edges}),'unresolved_edges':edges,
                  'limitations':['Offline predicate, no patient or clinical deployment.',
                    'No independently adjudicated medical reference; no sensitivity or specificity estimate.',
                    'No altered score, threshold, recommendation, alert or clinical status.',
                    'No recommendation to remove uncertainty weights or invent unresolved rules.'],
                  'records':records}
        artifact = output/'study.json'
        artifact.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        compact = {k:v for k,v in report.items() if k != 'records'}
        compact['study_file_sha256'] = hashlib.sha256(artifact.read_bytes()).hexdigest()
        (output/'summary.json').write_text(json.dumps(compact,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        print(json.dumps(compact,ensure_ascii=True,indent=2))


if __name__ == '__main__':
    main()
