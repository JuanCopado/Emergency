"""Unassigned synthetic document metadata needs an explicit scope decision."""
import unittest
from unittest.mock import patch

import test_blood_gas_review_contract as fixture
from blood_gas_review import samples


class MetadataScope(unittest.TestCase):
    def test_heading_spacing_literal_metadata_and_origin(self):
        padding = " " * 2048
        text = f"Muestra:\tVenosa  \nDate:  12:45  \npH 7.28{padding}[MeAsUrEd]  "
        group = samples(text, 1)[0]
        self.assertEqual([m["value"] for m in group["metadata"]], ["Venosa", "12:45  "])
        self.assertEqual(group["fields"][0]["origin"], "measured")
        self.assertEqual(group["fields"][0]["raw"], text.splitlines()[-1])
        self.assertEqual(samples("pH 7.28[measured]", 1)[0]["fields"][0]["origin"], "unknown")

    def prepare(self):
        case = fixture.ReviewContract()
        case.setUp()
        page = samples('Sample type: venous\nDate: 2026-11-18\nSample #A\npH 7.28', 1)[0]
        page.update(source_page=1, sample_label='A', region=[0, 0, 580, 220])
        page['fields'][0].update(legibility='unverified', bbox=[10, 10, 100, 30])
        case.page = page
        case.server.pages = [page]
        case.server.source = b'synthetic source'
        case.request['metadata'] = case.confirmed_metadata()
        return case

    def test_prefix_preserved_without_assigning_it_to_either_sample(self):
        groups = samples('Sample type: venous\nDate: 2026-11-18\nSample #A\npH 7.28\nSample #B\npH 7.41', 1)
        self.assertEqual(len(groups), 2)
        for group in groups:
            self.assertEqual([m['value'] for m in group['metadata']], ['venous', '2026-11-18'])
            self.assertTrue(all(m['scope'] == 'unassigned' for m in group['metadata']))
            self.assertNotIn('applies_to_sample', group['metadata'][0])

    def test_scope_decision_is_required_and_nonapplicability_has_a_reason(self):
        case = self.prepare()
        self.assertEqual(case.review()[0], 422)
        for item in case.request['metadata']:
            item['applies_to_sample'] = False
        self.assertEqual(case.review()[0], 422)
        for item in case.request['metadata']:
            item['reason'] = 'Synthetic header is not assigned to this sample'
        status, result = case.review()
        self.assertEqual(status, 200)
        self.assertTrue(all(m['scope'] == 'unassigned' and m['applies_to_sample'] is False
                            for m in result['reviewed_metadata']))
        case.request['metadata'][0]['applies_to_sample'] = 'false'
        self.assertEqual(case.review()[0], 422)

    def test_applicable_type_conflict_is_blocked_and_client_cannot_change_scope(self):
        case = self.prepare()
        for item in case.request['metadata']:
            item.update(applies_to_sample=True, scope='sample')
        case.request['sample'] = 'arterial'
        self.assertEqual(case.review()[0], 422)
        case.request['sample'] = 'venosa'
        self.assertEqual(case.review()[0], 200)
        del case.request['metadata'][0]['applies_to_sample']
        self.assertEqual(case.review()[0], 422)

    def test_manual_regions_keep_unassigned_document_context(self):
        case = self.prepare()
        new_page = samples('pH 7.28', 1)[0]
        new_page.update(source_page=1, sample_label='area', region=[0, 0, 580, 220])
        handler = fixture.InMemoryReview(case.server, dict(ticket='test-ticket',
            regions=[dict(page=1, bbox=[0, 0, 580, 220])]), '/regions')
        with patch('blood_gas_local.safe_extract', return_value=[new_page]):
            handler.handle_post()
        self.assertEqual(handler.response[0], 200)
        self.assertEqual([m['value'] for m in case.server.pages[0]['metadata']], ['venous', '2026-11-18'])
        self.assertTrue(all(m['scope'] == 'unassigned' for m in case.server.pages[0]['metadata']))

    def test_document_context_survives_temporarily_excluding_its_page(self):
        case = self.prepare()
        for page_number in (2, 1):
            page = samples('pH 7.28', page_number)[0]
            page.update(source_page=page_number, sample_label='area', region=[0, 0, 580, 220])
            handler = fixture.InMemoryReview(case.server, dict(ticket=case.server.ticket,
                regions=[dict(page=page_number, bbox=[0, 0, 580, 220])]), '/regions')
            with patch('blood_gas_local.safe_extract', return_value=[page]):
                handler.handle_post()
            self.assertEqual(handler.response[0], 200)
            if page_number == 2:
                self.assertEqual(case.server.pages[0]['metadata'], [])
        self.assertEqual([m['value'] for m in case.server.pages[0]['metadata']], ['venous', '2026-11-18'])


if __name__ == '__main__':
    unittest.main()
