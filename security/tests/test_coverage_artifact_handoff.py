"""Exercise the real workflow's artifact handoff across partial reruns.

The in-memory inventory models upload-artifact v4: names are scoped to a
workflow run, and overwrite replaces a complete artifact instead of merging it.
These tests do not execute Actions or claim a remote rerun was observed.
"""
import re
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
MODULES = ('portable', 't05', 't06')


def workflow(name):
    return yaml.load((ROOT / '.github/workflows' / name).read_text(encoding='utf8'),
                     Loader=yaml.BaseLoader)


def render(value, run_id, attempt, module):
    context = {'github.run_id': str(run_id), 'github.run_attempt': str(attempt),
               'matrix.module': module}
    return re.sub(r'\$\{\{\s*(.*?)\s*\}\}',
                  lambda match: context[match[1]], value)


class ArtifactHandoff:
    def __init__(self):
        security = workflow('security-and-quality.yml')['jobs']
        native = workflow('local-review-qa.yml')['jobs']['local-review']
        self.uploads = {
            'portable': next(step['with'] for step in security['coverage']['steps']
                             if step.get('uses', '').startswith('actions/upload-artifact@')
                             and '.coverage.portable' in step['with']['path']),
        }
        native_upload = next(step['with'] for step in native['steps']
                             if step.get('name') ==
                             'Publish measured native coverage after successful execution')
        self.uploads.update(t05=native_upload, t06=native_upload)
        destinations = {'.': 'portable', '.local-review/coverage-input/t05': 't05',
                        '.local-review/coverage-input/t06': 't06'}
        self.downloads = {
            destinations[step['with']['path']]: step['with']
            for step in security['sonarqube']['steps']
            if step.get('uses', '').startswith('actions/download-artifact@')
        }
        self.inventory = {}

    def publish(self, run_id, attempt, modules=MODULES):
        for module in modules:
            config = self.uploads[module]
            name = render(config['name'], run_id, attempt, module)
            key = (str(run_id), name)
            if key in self.inventory and config.get('overwrite', 'false') != 'true':
                raise FileExistsError('Artifact already exists: ' + name)
            # Each producer writes a distinguishable complete measurement bundle.
            self.inventory[key] = (run_id, module, attempt)

    def consume(self, run_id, attempt):
        result = {}
        for module, config in self.downloads.items():
            source_run = render(config.get('run-id', str(run_id)), run_id, attempt, module)
            name = render(config['name'], run_id, attempt, module)
            key = (source_run, name)
            if key not in self.inventory:
                raise FileNotFoundError('Missing measured coverage: ' + name)
            result[module] = self.inventory[key]
        return result


class CoverageArtifactHandoffTests(unittest.TestCase):
    def setUp(self):
        self.handoff = ArtifactHandoff()

    def assert_measurements(self, run_id, consumer_attempt, producer_attempts):
        expected = {module: (run_id, module, producer_attempts[module])
                    for module in MODULES}
        self.assertEqual(self.handoff.consume(run_id, consumer_attempt), expected)

    def test_first_attempt_receives_each_producers_measurements(self):
        self.handoff.publish(100, 1)
        self.assert_measurements(100, 1, dict.fromkeys(MODULES, 1))

    def test_only_t05_reruns_then_sonar_can_retry_without_new_measurements(self):
        self.handoff.publish(100, 1, ('portable', 't06'))
        with self.assertRaises(FileNotFoundError):
            self.handoff.consume(100, 1)
        self.handoff.publish(100, 2, ('t05',))
        expected = {'portable': 1, 't05': 2, 't06': 1}
        self.assert_measurements(100, 2, expected)
        self.assert_measurements(100, 3, expected)

    def test_rerun_portable_then_all_producers_replaces_old_measurements(self):
        self.handoff.publish(100, 1)
        self.handoff.publish(100, 2, ('portable',))
        self.assert_measurements(100, 2, {'portable': 2, 't05': 1, 't06': 1})
        self.handoff.publish(100, 3)
        self.assert_measurements(100, 3, dict.fromkeys(MODULES, 3))

    def test_another_runs_measurements_cannot_fill_a_missing_producer(self):
        self.handoff.publish(100, 1)
        with self.assertRaises(FileNotFoundError):
            self.handoff.consume(200, 1)
        self.handoff.publish(200, 1, ('portable', 't05'))
        with self.assertRaises(FileNotFoundError):
            self.handoff.consume(200, 1)
        self.handoff.publish(200, 1, ('t06',))
        self.handoff.publish(100, 2)
        self.assert_measurements(200, 1, dict.fromkeys(MODULES, 1))
        self.assert_measurements(100, 2, dict.fromkeys(MODULES, 2))


if __name__ == '__main__':
    unittest.main()
