"""Rebuild the portable demo from the same synthetic report as the local server."""
import json
from pathlib import Path

from demo_data import demo_invoices
from intelligence import score_invoices

ROOT = Path(__file__).resolve().parent


def inline(path):
    """Read a bundled asset without trailing whitespace in the generated HTML."""
    return '\n'.join(line.rstrip() for line in path.read_text(encoding='utf-8').splitlines())


report = score_invoices(demo_invoices())
data = 'window.CG_OFFLINE_REPORT = ' + json.dumps(report, ensure_ascii=False, separators=(',', ':')) + ';'
html = (ROOT / 'static/index.html').read_text(encoding='utf-8')
html = html.replace('<link rel="stylesheet" href="/vendor/ag-grid/styles/ag-grid.min.css"><link rel="stylesheet" href="/vendor/ag-grid/styles/ag-theme-quartz.min.css"><link rel="stylesheet" href="/style.css">',
                    '<style>' + inline(ROOT / 'static/vendor/ag-grid/styles/ag-grid.min.css') + inline(ROOT / 'static/vendor/ag-grid/styles/ag-theme-quartz.min.css') + inline(ROOT / 'static/style.css') + '</style>')
html = html.replace('<script defer src="/i18n.js"></script>',
                    '<script>' + (ROOT / 'static/i18n.js').read_text(encoding='utf-8') + '</script><script>' + data + '</script>')
html = html.replace('<script defer src="/vendor/ag-grid/ag-grid-community.min.js"></script><script defer src="/app.js"></script>',
                    '<script>' + inline(ROOT / 'static/vendor/ag-grid/ag-grid-community.min.js') + '</script><script>' + inline(ROOT / 'static/app.js') + '</script>')
html = html.replace('<script defer src="/settings.js"></script>', '<script>' + (ROOT / 'static/settings.js').read_text(encoding='utf-8') + '</script>')
html = html.replace('<script defer src="/workbench.js"></script>', '<script>' + (ROOT / 'static/workbench.js').read_text(encoding='utf-8') + '</script>')
license_text = (ROOT / 'static/vendor/ag-grid/LICENSE.txt').read_text(encoding='utf-8').strip()
html = html.replace('<!doctype html>', '<!doctype html>\n<!-- Bundled AG Grid Community 36.2.0 license:\n' + license_text + '\n-->', 1)
for name in ('Cashflow_Guardian_v0.9.html', 'Cashflow_Guardian_Demo.html'):
    (ROOT / name).write_text(html, encoding='utf-8')
print('Offline demo rebuilt from static/; v0.6 retained unchanged.')
