import io
from urllib.error import HTTPError
from paypal_client import _error_diagnostic

def error(body):
    return HTTPError('https://example.invalid',403,'Forbidden',{},io.BytesIO(body))

def test_error_diagnostic_identifiers_only():
    result=_error_diagnostic(error(b'{"name":"NOT_AUTHORIZED","debug_id":"abcdef1234567","message":"PRIVATE","access_token":"SECRET"}'))
    assert 'NOT_AUTHORIZED' in result and 'abcdef1234567' in result
    assert 'PRIVATE' not in result and 'SECRET' not in result

def test_error_diagnostic_handles_unexpected_payload():
    for body in [b'no json',b'[]',b'{"name":"<script>","debug_id":"private@example.com"}']:
        result=_error_diagnostic(error(body))
        assert 'unavailable' in result and '<script>' not in result and '@' not in result
