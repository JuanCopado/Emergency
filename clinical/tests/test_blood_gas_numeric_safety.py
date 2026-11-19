"""Synthetic checks: a complementary result must never carry Infinity/NaN."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from blood_gas_review import interpret, parse


class NumericSafety(unittest.TestCase):
    def test_extraction_rejects_numeric_overflow(self):
        with self.assertRaisesRegex(ValueError, 'finito'):
            parse('sO2 ' + '9' * 400 + ' %', 1)

    def test_confirmed_complementary_value_rejects_overflow(self):
        for sample in ('arterial', 'venosa'):
            with self.subTest(sample=sample), self.assertRaisesRegex(ValueError, 'finito'):
                interpret([
                    dict(name='pH', number='7.28', unit='', review='confirmed'),
                    dict(name='sO2', number='9' * 400, unit='%', review='confirmed'),
                ], sample)

    def test_extraction_does_not_turn_a_nonzero_literal_into_zero(self):
        for name, unit in (('HCO3', 'mmol/L'), ('pO2', 'mmHg'), ('sO2', '%'), ('BE', 'mmol/L')):
            for sign, separator in (('', '.'), ('-', '.'), ('', ',')):
                literal = sign + '0' + separator + '0' * 400 + '1'
                with self.subTest(name=name, sign=sign, separator=separator):
                    with self.assertRaisesRegex(ValueError, 'no representable'):
                        parse(name + ' ' + literal + ' ' + unit, 1)

    def test_manually_confirmed_nonzero_literal_cannot_underflow(self):
        for name, unit in (('HCO3', 'mmol/L'), ('pO2', 'mmHg'), ('sO2', '%'), ('BE', 'mmol/L')):
            for sample in ('arterial', 'venosa'):
                with self.subTest(name=name, sample=sample):
                    with self.assertRaisesRegex(ValueError, 'no representable'):
                        interpret([
                            dict(name='pH', number='7.28', unit='', review='confirmed'),
                            dict(name=name, number='0.' + '0' * 400 + '1', unit=unit, review='confirmed'),
                        ], sample)

    def test_explicit_zero_and_representable_subnormal_are_preserved(self):
        for literal in ('0', '-0', '0.000', '0,000'):
            rows = parse('pH 7.28\nBE ' + literal + ' mmol/L\nHCO3 0 mmol/L', 1)
            for row in rows:
                row['review'] = 'confirmed'
            result = interpret(rows, 'arterial')
            self.assertEqual(result['confirmed_values'][1]['number'], 0)
            self.assertEqual(result['confirmed_values'][2]['number'], 0)
        tiny = parse('BE 0.' + '0' * 323 + '5 mmol/L', 1)[0]
        self.assertGreater(tiny['numeric_value'], 0)

    def test_finite_values_retain_medical_review_and_canonical_result(self):
        rows = parse('pH 7.28\nsO2 98 %', 1)
        with self.assertRaises(ValueError):
            interpret(rows, 'arterial')
        for row in rows:
            row['review'] = 'confirmed'
        result = interpret(rows, 'arterial')
        self.assertEqual(result['ph_state'], 'acidemia')
        self.assertEqual(result['confirmed_values'][1]['number'], 98)


if __name__ == '__main__':
    unittest.main()
