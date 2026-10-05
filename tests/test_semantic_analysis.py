import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from docx import Document

from bot.application import build_services
from config import Settings
from models import DocumentMetadata
from processing.llm.ollama_provider import OllamaProvider
from processing.llm.quality import clean_metadata


class SemanticAnalysisTest(unittest.TestCase):
    def test_no_bank_fields_in_reminder_and_no_unconfirmed_address(self):
        result=DocumentMetadata(document_type='payment_reminder',title='raw',summary='raw',sender='Example GmbH',
            sender_address='Inventedstrasse 99, Berlin',amount='105.00',original_amount='105.00',
            transaction_type='return',due_date='2026-10-01')
        clean=clean_metadata(result,'Offener Betrag: 105,00 EUR')
        self.assertIsNone(clean.sender_address)
        self.assertIsNone(clean.transaction_type)
        self.assertIsNone(clean.original_amount)
        self.assertIn('Payment reminder',clean.title)
        self.assertTrue(clean.review_notes)

    def test_returned_debit_is_not_payment_request(self):
        result=DocumentMetadata(document_type='bank_transaction',title='raw',summary='raw',counterparty='Example GmbH',due_date='2026-10-01')
        clean=clean_metadata(result,'SEPA Lastschrift-Rückgabe')
        self.assertIsNone(clean.due_date)
        self.assertEqual(clean.transaction_type,'Returned direct debit (SEPA)')
        self.assertIn('Returned direct debit',clean.title)

    def test_local_only_and_structured_response(self):
        with self.assertRaises(ValueError):
            OllamaProvider('https://external.example','model')
        result=DocumentMetadata(document_type='bank_transaction',title='Returned direct debit',summary='The bank recorded a returned direct debit.',counterparty='Example GmbH',amount='71.97',currency='EUR')
        response=MagicMock()
        response.read.return_value=json.dumps({'message':{'content':result.model_dump_json()},'done_reason':'stop'}).encode()
        response.__enter__.return_value=response
        with patch('urllib.request.urlopen',return_value=response) as call:
            actual=OllamaProvider('http://127.0.0.1:11435','test-model').extract_metadata('Source','a.txt')
        self.assertEqual(actual.counterparty,'Example GmbH')
        self.assertIsNone(actual.sender)
        payload=json.loads(call.call_args.args[0].data)
        self.assertEqual(payload['options']['temperature'],0)
        self.assertIn('recipient_address',payload['format']['properties'])

    def test_reanalysis_preserves_id_and_ocr_and_updates_index(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            source=root/'invoice.docx'
            document=Document();document.add_paragraph('Invoice Total: 42.00 EUR');document.save(source)
            pipeline,db=build_services(Settings(_env_file=None,llm_provider='mock',ocr_provider='disabled',data_dir=root/'data',database_path=root/'data/documents.db'))
            first=pipeline.process(source,source.name,1).document
            raw=Path(first.text_path).read_bytes()
            improved=DocumentMetadata(document_type='invoice',title='Clean example invoice',summary='One invoice.',sender='Example Ltd',recipient_address='Test Street 1',amount='42.00',currency='EUR')
            with patch.object(pipeline.extractor,'extract',side_effect=AssertionError('OCR must not repeat')):
                with patch.object(pipeline.llm,'analyze_document',return_value=improved):
                    updated=pipeline.reanalyze(first).document
            self.assertEqual(updated.id,first.id)
            self.assertEqual(Path(updated.text_path).read_bytes(),raw)
            self.assertEqual(db.recent(1)[0].metadata.title,'Clean example invoice')
            self.assertEqual(len(db.search(1,'Clean')),1)
            self.assertEqual(len(list((root/'data/history'/first.id).glob('*.json'))),1)
