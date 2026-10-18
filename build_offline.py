"""Rebuild the portable demo from the same files used by the local server."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
original = (ROOT / 'Cashflow_Guardian_v0.6.html').read_text(encoding='utf-8')
data = next(s for s in re.findall(r'<script[^>]*>(.*?)</script>', original, re.S)
            if 'window.CG_OFFLINE_REPORT =' in s)
html = (ROOT / 'static/index.html').read_text(encoding='utf-8')
html = html.replace('<link rel="stylesheet" href="/style.css">',
                    '<style>' + (ROOT / 'static/style.css').read_text(encoding='utf-8') + '</style>')
html = html.replace('<script defer src="/i18n.js"></script>',
                    '<script>' + (ROOT / 'static/i18n.js').read_text(encoding='utf-8') + '</script><script>' + data + '</script>')
html = html.replace('<script defer src="/app.js"></script>',
                    '<script>' + (ROOT / 'static/app.js').read_text(encoding='utf-8') + '</script>')
html = html.replace('<script defer src="/settings.js"></script>', '<script>' + (ROOT / 'static/settings.js').read_text(encoding='utf-8') + '</script>')
html = html.replace('<script defer src="/workbench.js"></script>', '<script>' + (ROOT / 'static/workbench.js').read_text(encoding='utf-8') + '</script>')
for name in ('Cashflow_Guardian_v0.9.html', 'Cashflow_Guardian_Demo.html'):
    (ROOT / name).write_text(html, encoding='utf-8')
print('Offline demo rebuilt from static/; v0.6 retained unchanged.')
