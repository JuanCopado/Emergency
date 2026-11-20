"""Non-prescriptive country/topic evidence directory for Emergency INT-02/INT-03.

No dose, protocol selection, product authorization or clinical release is inferred.
Country selection is mandatory only for this explicit country-comparison utility.
The international clinical core requires no country; language is never a country input.
"""
import argparse
import json
from pathlib import Path

INDEX = Path(__file__).resolve().parents[1] / 'references' / 'international-country-topic-matrix.json'
PENDING = 'PENDING_JURISDICTION_RECONCILIATION'
REFERENCE = 'DOCUMENTARY_REVIEWED_REFERENCE_ONLY'
CONFLICT = 'CONFLICTING_REVIEW_RECORDS'
REQUIRED_REVIEW = (
    'country_code', 'topic_id', 'indication', 'population', 'setting',
    'source_url', 'source_title', 'source_version', 'source_date',
    'verified_at', 'reviewer_clinical',
)


def load_matrix(path=INDEX):
    """Load a directory, not a therapeutic protocol or a release manifest."""
    raw = json.loads(Path(path).read_text(encoding='utf-8'))
    if raw.get('clinical_release_status') != 'CLINICALLY_PENDING':
        raise ValueError('Unexpected clinical release declaration in directory')
    countries = raw.get('countries')
    topics = raw.get('topics')
    if not isinstance(countries, list) or not isinstance(topics, list):
        raise ValueError('Directory must contain country and topic arrays')
    country_codes = [c.get('code') for c in countries]
    topic_ids = [t.get('id') for t in topics]
    if len(country_codes) != len(set(country_codes)) or len(topic_ids) != len(set(topic_ids)):
        raise ValueError('Duplicate country or topic identifier')
    if not country_codes or not topic_ids:
        raise ValueError('Empty directory')
    for country in countries:
        if not isinstance(country.get('registry_url'), str) or not country['registry_url'].startswith('https://'):
            raise ValueError('Regulatory directory URL must use HTTPS')
    for review in raw.get('country_topic_reviews', []):
        if review.get('country_code') not in country_codes or review.get('topic_id') not in topic_ids:
            raise ValueError('Review refers to unknown country/topic')
    return raw


def compare_topic(topic_id, countries, matrix=None, *, language=None):
    """Compare national review coverage only, NEVER provide clinical dose or regimen.

    A reviewed reference is not an authorization to use, prescribe or calculate.
    An explicit organization/product/indication gate must exist in a separate
    clinically validated workflow before any medication calculator can use it.
    """
    matrix = load_matrix() if matrix is None else matrix
    catalog_countries = {c['code']: c for c in matrix['countries']}
    catalog_topics = {t['id']: t for t in matrix['topics']}
    if topic_id not in catalog_topics:
        raise ValueError('Unknown topic')
    if not isinstance(countries, (tuple, list)) or not countries:
        raise ValueError('Explicit country list is required; no implicit default')
    if any(not isinstance(code, str) or code not in catalog_countries for code in countries):
        raise ValueError('Unknown or missing ISO 3166-1 alpha-2 country')
    if len(set(countries)) != len(countries):
        raise ValueError('Repeated country')
    topic = catalog_topics[topic_id]
    result = []
    for code in countries:
        matches = [r for r in matrix.get('country_topic_reviews', [])
                   if r.get('country_code') == code and r.get('topic_id') == topic_id]
        # Separate presentations and indications can coexist in one country.
        scopes = [(r.get('product'), r.get('presentation'), r.get('indication'),
                   r.get('population'), r.get('setting')) for r in matches]
        conflict = len(scopes) != len(set(tuple(str(v) for v in scope) for scope in scopes))
        reviewed = bool(matches) and all(
            r.get('review_status') == 'DOCUMENTARY_REVIEWED'
            and all(isinstance(r.get(key), str) and r[key].strip() for key in REQUIRED_REVIEW)
            and r['source_url'].startswith('https://') for r in matches)
        status = CONFLICT if conflict else REFERENCE if reviewed else PENDING
        country = catalog_countries[code]
        result.append({
            'country_code': code,
            'country': country['name_es'],
            'regulatory_authority': country['authority'],
            'regulatory_directory': country['registry_url'],
            'source_review_status': status,
            'clinical_release_status': 'CLINICALLY_PENDING',
            'clinical_use_permitted': False,
            'dose': None,
            'preparation': None,
            'recommendation': None,
        })
    return {'topic_id': topic_id, 'topic': topic['name_es'], 'kind': topic['kind'],
            'language_used_for_country_selection': False,
            'country_comparison': result,
            'warning': 'Directorio no prescriptivo. Ningún país ni producto validado para uso asistencial por esta matriz.'}


def main():
    parser = argparse.ArgumentParser(description='Compare directory coverage; no clinical dosing')
    parser.add_argument('--topic', required=True)
    parser.add_argument('--country', action='append', required=True)
    args = parser.parse_args()
    print(json.dumps(compare_topic(args.topic, args.country), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
