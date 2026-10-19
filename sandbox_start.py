"""Enter sandbox credentials locally; secrets stay in this process only."""
import getpass
import os
from paypal_client import get_invoices, PayPalError
from intelligence import score_invoices
from server import start

if __name__ == '__main__':
    print('PayPal SANDBOX only. No real payments. Credentials are not saved.')
    try:
        os.environ['PAYPAL_SANDBOX_CLIENT_ID'] = getpass.getpass('Sandbox Client ID (hidden): ').strip()
        os.environ['PAYPAL_SANDBOX_CLIENT_SECRET'] = getpass.getpass('Sandbox Secret (hidden): ').strip()
        rows = get_invoices()
        result = score_invoices(rows)
        print(f"Sandbox connection verified: {len(rows)} invoices; {len(result['duplicates'])} review candidates.")
        if not rows:
            print('No invoices returned. Create sandbox test invoices before recording the demonstration.')
        print('Open http://127.0.0.1:8765 and choose PayPal Sandbox.')
        start()
    except (PayPalError, ValueError) as exc:
        print(str(exc))
        raise SystemExit(1)
    finally:
        os.environ.pop('PAYPAL_SANDBOX_CLIENT_ID', None)
        os.environ.pop('PAYPAL_SANDBOX_CLIENT_SECRET', None)
