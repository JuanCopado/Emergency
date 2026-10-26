import fnmatch
import runpy
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def workflow(name):
    # BaseLoader keeps the Actions key "on" a string (YAML 1.1 treats it as bool).
    return yaml.load((ROOT / '.github/workflows' / name).read_text(encoding='utf-8'), Loader=yaml.BaseLoader)


class WorkflowCoverageTests(unittest.TestCase):
    def test_all_workflows_parse_and_checkout_same_event_commit(self):
        for path in (ROOT / '.github/workflows').glob('*.yml'):
            data = workflow(path.name)
            self.assertIn('on', data, path.name)
            self.assertIn('jobs', data, path.name)
            for job in data['jobs'].values():
                for step in job.get('steps', []):
                    if step.get('uses', '').startswith('actions/checkout@'):
                        self.assertNotIn('ref', step.get('with', {}), path.name)

    def test_clinical_and_ui_trigger_for_v142_and_relevant_paths(self):
        paths = {
            'clinical-qa.yml': ['clinical/calculators/registry.json', 'clinical/data/example.json',
                                'clinical/schemas/example.json', 'clinical/templates/example.md',
                                'clinical/requirements-test.txt', 'clinical/assets/fonts/DejaVuSans.ttf',
                                'clinical/tests/test_clinical_scores_registry.py'],
            'app-ui-qa.yml': ['app/src/pages/ClinicalLibrary.tsx', 'clinical/modules/procedures/02-vascular-monitoring.md',
                             'clinical/modules/emergency-procedures-index.md', 'clinical/references/module-index.md',
                             'clinical/MODULES.md', 'clinical/references/evidence-registry.json', 'clinical/requirements-test.txt',
                             'clinical/qa/pediatric-outpatient-medications.json',
                             'clinical/qa/pediatric-outpatient-alert-rules.json'],
        }
        for name, changed_paths in paths.items():
            for event in ('push', 'pull_request'):
                config = workflow(name)['on'][event]
                self.assertNotIn('paths-ignore', config)
                for branch in ('main', 'v1.39-clinical-note-diagnostic-support', 'v1.42-codex-consolidation'):
                    self.assertTrue(any(fnmatch.fnmatchcase(branch, pattern) for pattern in config.get('branches', ['*'])), (name, event, branch))
                for path in changed_paths:
                    self.assertTrue(any(fnmatch.fnmatchcase(path, pattern) for pattern in config['paths']), (name, event, path))

    def test_codex_push_branches_and_architecture_paths(self):
        branches = ('codex/v144-t01-architecture-ci', 'codex/team/nested-task',
                    'main', 'v1.44-clinical-functional-validation')
        cases = {
            'clinical-qa.yml': ('clinical/scripts/normalize_evidence_sources.py',
                'clinical/references/evidence-sources.json', 'docs/ARCHITECTURE.md',
                'knowledge-graph/README.md', 'rag/README.md', 'models/MODEL_REGISTRY.md',
                '.graphifyignore', '.github/workflows/clinical-qa.yml'),
            'app-ui-qa.yml': ('app/src/pages/Home.tsx', '.github/workflows/app-ui-qa.yml'),
            'v1.40-evidence-surveillance-qa.yml': ('clinical/references/evidence-sources.json',),
        }
        for name, paths in cases.items():
            for event in ('push', 'pull_request'):
                config = workflow(name)['on'][event]
                for branch in branches:
                    self.assertTrue(any(fnmatch.fnmatchcase(branch, pattern)
                        for pattern in config.get('branches', ['*'])), (name, event, branch))
                for path in paths:
                    self.assertTrue(any(fnmatch.fnmatchcase(path, pattern)
                        for pattern in config['paths']), (name, event, path))
        for name in cases:
            self.assertFalse(any(fnmatch.fnmatchcase('unrelated/task', pattern)
                for pattern in workflow(name)['on']['push']['branches']))

    def test_technical_checks_preserve_existing_qa(self):
        clinical = '\n'.join(step.get('run', '') for step in
            workflow('clinical-qa.yml')['jobs']['qa']['steps'])
        for command in ('normalize_evidence_sources.py --check', 'qa/qa_runner.py',
                        'build_project_graph.py --output'):
            self.assertIn(command, clinical)
        app = '\n'.join(step.get('run', '') for step in
            workflow('app-ui-qa.yml')['jobs']['ui']['steps'])
        self.assertIn('npm run lint', app)
        self.assertIn('node --test scripts/write-qa-evidence.node-test.mjs', app)
        # Specialized intake and scheduled surveillance must not become push CI.
        for name in ('evidence-surveillance.yml', 'urgent-medication-safety-surveillance.yml'):
            self.assertNotIn('push', workflow(name)['on'])
        self.assertEqual(workflow('ptbxl-blinded-intake.yml')['on']['push']['branches'],
                         ['v1.36-consolidation'])

    def test_python_requirements_installed_before_qa(self):
        for name, job_name in [('clinical-qa.yml', 'qa'), ('app-ui-qa.yml', 'ui')]:
            steps = workflow(name)['jobs'][job_name]['steps']
            installs = [i for i, step in enumerate(steps) if 'pip install -r' in step.get('run', '') and 'requirements-test.txt' in step['run']]
            self.assertEqual(len(installs), 1, name)
            setup = next(step for step in steps if step.get('uses', '').startswith('actions/setup-python@'))
            self.assertEqual(setup['with']['cache'], 'pip')
            self.assertIn('clinical/requirements.txt', setup['with']['cache-dependency-path'])
            self.assertIn('clinical/requirements-test.txt', setup['with']['cache-dependency-path'])
            run_index = next(i for i, step in enumerate(steps) if 'qa_runner.py' in step.get('run', '') or 'guides:print-check' in step.get('run', ''))
            self.assertLess(installs[0], run_index)
        self.assertIn('-r requirements.txt', (ROOT / 'clinical/requirements-test.txt').read_text())

    def test_unified_runner_covers_every_suite_exactly_once(self):
        checks = runpy.run_path(str(ROOT / 'clinical/qa/qa_runner.py'))['CHECKS']
        commands = [command for _, command in checks if 'unittest' in command]
        for path in (ROOT / 'clinical/tests').glob('test_*.py'):
            matches = 0
            for command in commands:
                if 'discover' in command:
                    pattern = command[command.index('-p') + 1] if '-p' in command else 'test*.py'
                    matches += fnmatch.fnmatchcase(path.name, pattern)
                else:
                    matches += any(Path(arg).name == path.name for arg in command)
            self.assertEqual(matches, 1, path.name)

    def test_ui_runs_fidelity_and_production_checks(self):
        steps = workflow('app-ui-qa.yml')['jobs']['ui']['steps']
        commands = '\n'.join(step.get('run', '') for step in steps)
        for required in ('npm ci', 'npm test', 'npm run typecheck', 'npm run build',
                         'npm run guides:test', 'npm run procedures:test', 'npm run guides:print-check',
                         'npm run pediatrics:check', 'npm run pediatrics:browser-check'):
            self.assertIn(required, commands)

    def test_surveillance_guard_covers_v142_without_duplicate_pr_tests(self):
        data = workflow('v1.40-evidence-surveillance-qa.yml')
        for event in ('push', 'pull_request'):
            self.assertTrue(any(fnmatch.fnmatchcase('v1.42-codex-consolidation', p)
                                for p in data['on'][event].get('branches', ['*'])))
        steps = data['jobs']['qa']['steps']
        for step in steps:
            if 'unittest' in step.get('run', ''):
                self.assertIn("github.event_name == 'workflow_dispatch'", step.get('if', ''))
        self.assertTrue(any('Forbidden automatic mutation' in step.get('run', '') for step in steps))
