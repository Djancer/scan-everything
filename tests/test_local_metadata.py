import unittest
from processing.llm.local_provider import LocalMetadataProvider


class LocalMetadataTest(unittest.TestCase):
    def test_explicit_total_and_unknown_fields(self):
        data = LocalMetadataProvider().extract_metadata('Invoice\nTotal: 1.234,56 EUR\n2026-09-23', 'a.pdf')
        self.assertEqual(str(data.amount), '1234.56')
        self.assertEqual(data.currency, 'EUR')
        self.assertIsNone(data.sender)
        self.assertEqual(data.date, '2026-09-23')

    def test_arbitrary_amount_is_not_total(self):
        data = LocalMetadataProvider().extract_metadata('Contract\nOne item costs 25.00 EUR', 'a.pdf')
        self.assertIsNone(data.amount)
