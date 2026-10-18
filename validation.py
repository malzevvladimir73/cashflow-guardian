"""Bounded, strict import validation. Imported records are never saved to disk."""
from datetime import date
from decimal import Decimal, InvalidOperation
import re

STATUSES = {'SENT', 'UNPAID', 'PARTIALLY_PAID', 'PAYMENT_PENDING', 'OVERDUE',
            'PAID', 'DRAFT', 'CANCELLED', 'REFUNDED', 'PARTIALLY_REFUNDED', 'MARKED_AS_PAID'}

def validate_invoices(payload):
    if not isinstance(payload, list) or not 1 <= len(payload) <= 1000:
        raise ValueError('Import requires 1–1000 invoice records.')
    result, identifiers = [], set()
    for index, record in enumerate(payload, 1):
        def fail(field):
            raise ValueError(f'Row {index}: invalid {field}.')
        if not isinstance(record, dict):
            fail('record')
        row = {}
        for key, maximum in [('number', 100), ('customer', 200), ('description', 1000)]:
            value = record.get(key, '')
            if not isinstance(value, str) or len(value) > maximum or (key != 'description' and not value.strip()):
                fail(key)
            row[key] = value.strip()
        if row['number'] in identifiers:
            fail('duplicate invoice number')
        identifiers.add(row['number'])
        row['id'] = row['number']
        for key in ['issued', 'due']:
            value = record.get(key, '')
            if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                fail(key)
            try:
                date.fromisoformat(value)
            except ValueError:
                fail(key)
            row[key] = value
        row['currency'] = str(record.get('currency', '')).upper()
        if not re.fullmatch('[A-Z]{3}', row['currency']):
            fail('currency')
        row['status'] = str(record.get('status', '')).upper()
        if row['status'] not in STATUSES:
            fail('status')
        for key in ['amount', 'due_amount']:
            value = record.get(key)
            if key == 'due_amount' and value in (None, ''):
                value = 0 if row['status'] in ('PAID', 'MARKED_AS_PAID') else row['amount']
            try:
                amount = Decimal(str(value))
                if not amount.is_finite() or amount < 0 or amount > Decimal('1000000000'):
                    fail(key)
                row[key] = float(amount)
            except (InvalidOperation, TypeError):
                fail(key)
        if row['due_amount'] > row['amount']:
            fail('due_amount exceeds amount')
        if row['status'] in ('PAID', 'MARKED_AS_PAID') and row['due_amount'] != 0:
            fail('paid invoice has an outstanding amount')
        row['source'] = 'local import'
        result.append(row)
    return result
