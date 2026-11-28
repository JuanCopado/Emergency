"""Regression checks for boundaries lost when combining the reviewed branches."""
import hashlib
import json
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


class R3IntegrationTests(unittest.TestCase):
    def test_every_product_command_keeps_a_fail_closed_prehook(self):
        scripts = json.loads((ROOT / 'app/package.json').read_text(encoding='utf-8'))['scripts']
        products = [name for name in scripts if name != 'postinstall'
                    and not name.startswith('security:')
                    and not (name.startswith('pre') and name[3:] in scripts)]
        self.assertIn('i18n:browser-check', products)
        self.assertIn('build:security', products)
        for name in products:
            with self.subTest(command=name):
                expected = ('node scripts/check-dermatology-asset-admission.mjs && '
                            'node scripts/picomatch-mitigation.mjs --check'
                            if name in ('dev', 'build')
                            else 'node scripts/picomatch-mitigation.mjs --check')
                self.assertEqual(scripts.get('pre' + name), expected)
        self.assertEqual(scripts['security:dermatology:check'],
                         'node scripts/check-dermatology-asset-admission.mjs')
        self.assertEqual(scripts['security:dermatology:test'],
                         'node --test scripts/dermatology-asset-admission.node-test.mjs')

    def test_rollup_extension_uses_the_exact_reviewed_lock_and_policy(self):
        config = json.loads((ROOT / 'security/picomatch-mitigation.json').read_text(encoding='utf-8'))
        for name, key in [('app/package-lock.json', 'lock_sha256'),
                          ('app/scripts/picomatch-runtime-policy.cjs', 'policy_sha256')]:
            data = (ROOT / name).read_bytes().replace(b'\r\n', b'\n')
            self.assertEqual(hashlib.sha256(data).hexdigest(), config[key])
        self.assertEqual(len(config['targets']), 14)
        self.assertEqual(sum(item.get('parsers', 0) for item in config['targets']
                             if item['package'] == 'node_modules/rollup'), 6)

    def test_product_ci_keeps_audited_install_and_authoritative_scanner_database(self):
        for filename in ['app-ui-qa.yml', 'security-and-quality.yml']:
            text = (ROOT / '.github/workflows' / filename).read_text(encoding='utf-8')
            parsed = yaml.safe_load(text)
            for job in parsed['jobs'].values():
                commands = '\n'.join(str(step.get('run', '')) for step in job.get('steps', []))
                if 'npm ci' in commands:
                    self.assertIn('npm ci --ignore-scripts --no-audit --no-fund', commands)
                    self.assertTrue('npm run postinstall --ignore-scripts' in commands
                                    or 'npm run security:picomatch:apply --prefix app' in commands)
        text = (ROOT / '.github/workflows/security-and-quality.yml').read_text(encoding='utf-8')
        self.assertIn('--db-repository ghcr.io/aquasecurity/trivy-db:2', text)
        self.assertIn('node scripts/check-picomatch-coverage.mjs --run', text)

    def test_python_security_checks_install_their_locked_runtime_first(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/security-and-quality.yml').read_text(encoding='utf-8'))
        steps = workflow['jobs']['semgrep']['steps']
        check = next(i for i, step in enumerate(steps)
                     if 'unittest discover -s security/tests' in str(step.get('run', '')))
        preceding = steps[:check]
        self.assertTrue(any(step.get('uses', '').startswith('actions/setup-python@')
                            and step.get('with', {}).get('python-version') == '3.12'
                            for step in preceding))
        self.assertTrue(any('python -m pip install --only-binary=:all: --require-hashes -r security/requirements-ci.txt'
                            in str(step.get('run', '')) for step in preceding))

    def test_build_still_checks_production_modules_and_service_worker(self):
        vite = (ROOT / 'app/vite.config.ts').read_text(encoding='utf-8')
        self.assertIn('productionDependencyGuard()', vite)
        self.assertIn('sourcemap: auditBuild', vite)
        scripts = json.loads((ROOT / 'app/package.json').read_text(encoding='utf-8'))['scripts']
        self.assertIn('--check-service-worker', scripts['build:security'])
        workflow = yaml.safe_load((ROOT / '.github/workflows/app-ui-qa.yml').read_text(encoding='utf-8'))
        builds = [step for job in workflow['jobs'].values() for step in job.get('steps', [])
                  if step.get('name') == 'Build']
        self.assertEqual(len(builds), 1)
        self.assertEqual(builds[0]['run'], 'npm run build:security')
        self.assertEqual(builds[0]['env']['EMERGENCY_SECURITY_AUDIT'], '1')


if __name__ == '__main__':
    unittest.main()
