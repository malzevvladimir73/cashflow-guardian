import json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
S=(ROOT/'static'/'i18n.js').read_text(encoding='utf-8')
def obj(name):
  prefix='const '+name+' = '
  return json.JSONDecoder().raw_decode(S[S.index(prefix)+len(prefix):])[0]
def test_all_locales_have_translations():
  langs=obj('CG_LANGUAGES'); translations=obj('CG_TRANSLATIONS'); descriptions=obj('CG_DEMO_DESCRIPTIONS')
  assert len(langs)==12
  assert 'ar' not in langs
  assert langs['pt']['flag']=='🇵🇹'
  assert {'de','pl','ro','nl','pt'} <= set(langs)
  for lang in langs:
    assert set(translations[lang]) == set(translations['en'])
    assert len(descriptions[lang])==15
    assert all(not str(x).strip().startswith('undefined') for x in translations[lang].values())
def test_portuguese_locale_and_ltr():
  assert "pt:'pt-PT'" in S
  assert "html.dir='ltr'" in S
def test_standalone_flags_are_embedded():
  s=(ROOT/'Cashflow_Guardian_v0.8.html').read_text(encoding='utf-8')
  assert 'const CG_FLAG_IMAGES' in s
  assert 'data:image/png;base64,' in s
  assert "pt:'pt-PT'" in s
  assert 'pt-BR' not in s
