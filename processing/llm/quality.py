"""Conservative checks and clear English presentation after model extraction."""
import re
import unicodedata
from datetime import date
from difflib import SequenceMatcher

from models import DocumentMetadata


def words(text):
    return re.findall(r'[^\W\d_]+',unicodedata.normalize('NFKD',text.casefold()),re.UNICODE)


def address_supported(address, text):
    """A legible OCR street token must support a proposed postal address.

    Names guessed only from a blurry photo remain unconfirmed instead of silently
    entering the archive as authoritative. This deliberately favours abstention.
    """
    street=address.split(',')[0]
    meaningful=[w for w in words(street) if len(w)>=5]
    source=words(text)
    return bool(meaningful) and all(any(SequenceMatcher(None,w,s).ratio()>=.84 for s in source) for w in meaningful)


def clean_metadata(metadata: DocumentMetadata, text: str) -> DocumentMetadata:
    notes=[]
    for name,label in [('sender_address','sender'),('recipient_address','recipient')]:
        address=getattr(metadata,name)
        if address and not address_supported(address,text):
            setattr(metadata,name,None)
            notes.append('The '+label+' address is not supported by OCR; check the original.')
    for name in ('date','invoice_date','due_date'):
        value=getattr(metadata,name)
        if value:
            try:
                date.fromisoformat(value)
            except ValueError:
                setattr(metadata,name,None)
                notes.append('A date could not be parsed reliably.')
    if metadata.original_amount == metadata.amount:
        metadata.original_amount=None
    if metadata.document_type != 'bank_transaction':
        metadata.transaction_type=None
    titles={'payment_reminder':'Payment reminder','invoice':'Invoice','bank_transaction':'Bank transaction',
            'contract':'Contract','receipt':'Receipt','letter':'Letter','other':'Document'}
    org=metadata.counterparty if metadata.document_type=='bank_transaction' else metadata.sender
    label=titles.get(metadata.document_type,'Document')
    if metadata.document_type=='payment_reminder':
        metadata.summary='This letter is a reminder about an unpaid invoice.'
        if metadata.due_date:
            metadata.summary+=' The stated payment deadline is '+date.fromisoformat(metadata.due_date).strftime('%d.%m.%Y')+'.'
        metadata.tags=['reminder','payment']
    elif metadata.document_type=='bank_transaction':
        metadata.original_amount=None
        metadata.invoice_date=None
        metadata.due_date=None
        if re.search(r'lastschrift[\s\-–]*r[üu]ckgabe',text,re.I):
            label='Returned direct debit'
            metadata.transaction_type='Returned direct debit (SEPA)'
            metadata.summary='Bank record of a returned direct debit'+(' involving '+org if org else '')+'.'
            metadata.tags=['bank transaction','return','SEPA']
        else:
            metadata.summary='Bank transaction'+(' involving '+org if org else '')+'. See the structured fields for details.'
            metadata.tags=['bank transaction']
    elif metadata.document_type=='invoice':
        metadata.summary='Invoice'+(' from '+org if org else '')+'. See the structured fields for the amount, date, and parties.'
        metadata.tags=['invoice','payment']
    metadata.title=label+(' · '+org if org else (' # '+metadata.document_number if metadata.document_number else ''))
    if metadata.review_notes and not notes:
        notes.append('Some source text is unclear. Check important details against the original.')
    metadata.review_notes=list(dict.fromkeys(notes))
    return metadata
