'use strict';
const CG_SETTING_KEYS=['settings','dateFormat','automatic','region','preview','currency','start','group','columns','density','comfortable','compact','reset','saved','local','shortNote','storageError'];
const CG_SETTING_TEXT={
de:['Einstellungen','Datumsformat','Automatisch (Browserregion)','Browserregion','Vorschau','Standardwährung','Startansicht','Standardgruppierung','Tabellenspalten','Zeilenabstand','Großzügig','Kompakt','Standard wiederherstellen','Gespeichert','Einstellungen bleiben in diesem Browser. Keine Standort- oder IP-Abfrage.','Ohne Jahreszahl: Das vollständige Datum erscheint beim Darüberfahren.','Speichern ist in diesem Browser nicht verfügbar. Einstellungen gelten bis zum Schließen.'],
en:['Settings','Date format','Automatic (browser region)','Browser region','Preview','Default currency','Start view','Default grouping','Table columns','Row spacing','Comfortable','Compact','Restore defaults','Saved','Settings stay in this browser. No location or IP lookup.','Without year: hover to see the complete date.','Storage is unavailable in this browser. Settings apply until you close it.'],
es:['Ajustes','Formato de fecha','Automático (región del navegador)','Región del navegador','Vista previa','Moneda predeterminada','Vista inicial','Agrupación predeterminada','Columnas','Espaciado','Amplio','Compacto','Restablecer valores','Guardado','Los ajustes se guardan en este navegador. Sin consultar ubicación ni IP.','Sin año: pasa el cursor para ver la fecha completa.','No se puede guardar. Los ajustes duran hasta cerrar el navegador.'],
fr:['Paramètres','Format de date','Automatique (région du navigateur)','Région du navigateur','Aperçu','Devise par défaut','Vue initiale','Regroupement par défaut','Colonnes','Espacement','Confortable','Compact','Rétablir les valeurs','Enregistré','Réglages conservés dans ce navigateur. Aucune recherche de position ou IP.','Sans année : survolez pour afficher la date complète.','Stockage indisponible. Réglages valables jusqu’à la fermeture.'],
pt:['Definições','Formato de data','Automático (região do navegador)','Região do navegador','Pré-visualização','Moeda predefinida','Vista inicial','Agrupamento predefinido','Colunas','Espaçamento','Confortável','Compacto','Repor predefinições','Guardado','Definições neste navegador. Sem consulta de localização ou IP.','Sem ano: passe o cursor para ver a data completa.','Não é possível guardar. Definições válidas até fechar o navegador.'],
it:['Impostazioni','Formato data','Automatico (regione del browser)','Regione del browser','Anteprima','Valuta predefinita','Vista iniziale','Raggruppamento predefinito','Colonne','Spaziatura','Ampia','Compatta','Ripristina valori','Salvato','Impostazioni in questo browser. Nessuna ricerca di posizione o IP.','Senza anno: passa il mouse per vedere la data completa.','Salvataggio non disponibile. Impostazioni valide fino alla chiusura.'],
pl:['Ustawienia','Format daty','Automatyczny (region przeglądarki)','Region przeglądarki','Podgląd','Domyślna waluta','Widok początkowy','Domyślne grupowanie','Kolumny','Odstępy','Przestronnie','Kompaktowo','Przywróć domyślne','Zapisano','Ustawienia pozostają w przeglądarce. Bez sprawdzania lokalizacji lub IP.','Bez roku: najedź kursorem, aby zobaczyć pełną datę.','Zapis niedostępny. Ustawienia działają do zamknięcia przeglądarki.'],
ro:['Setări','Formatul datei','Automat (regiunea browserului)','Regiunea browserului','Previzualizare','Monedă implicită','Vizualizare inițială','Grupare implicită','Coloane','Spațiere','Aerisit','Compact','Restabilește valorile','Salvat','Setările rămân în browser. Fără verificarea locației sau IP-ului.','Fără an: treci cursorul pentru data completă.','Salvarea nu este disponibilă. Setările se păstrează până la închidere.'],
nl:['Instellingen','Datumnotatie','Automatisch (browserregio)','Browserregio','Voorbeeld','Standaardvaluta','Startweergave','Standaardgroepering','Kolommen','Rijafstand','Ruim','Compact','Standaard herstellen','Opgeslagen','Instellingen blijven in deze browser. Geen locatie- of IP-opvraag.','Zonder jaar: wijs de datum aan voor de volledige datum.','Opslaan is niet beschikbaar. Instellingen gelden tot het sluiten.'],
zh:['设置','日期格式','自动（浏览器地区）','浏览器地区','预览','默认货币','起始视图','默认分组','表格列','行间距','宽松','紧凑','恢复默认设置','已保存','设置保存在此浏览器中。不查询位置或 IP。','不显示年份：悬停可查看完整日期。','无法保存。设置在关闭浏览器前有效。'],
hi:['सेटिंग्स','दिनांक प्रारूप','स्वचालित (ब्राउज़र क्षेत्र)','ब्राउज़र क्षेत्र','पूर्वावलोकन','डिफ़ॉल्ट मुद्रा','प्रारंभिक दृश्य','डिफ़ॉल्ट समूह','तालिका कॉलम','पंक्ति अंतर','खुला','सघन','डिफ़ॉल्ट बहाल करें','सहेजा गया','सेटिंग्स इसी ब्राउज़र में रहती हैं। स्थान या IP की जाँच नहीं होती।','वर्ष के बिना: पूरी तारीख देखने के लिए होवर करें।','सहेजना उपलब्ध नहीं है। सेटिंग्स ब्राउज़र बंद करने तक लागू हैं।'],
ja:['設定','日付形式','自動（ブラウザーの地域）','ブラウザーの地域','プレビュー','既定の通貨','開始画面','既定のグループ','表の列','行間隔','ゆったり','コンパクト','既定値に戻す','保存済み','設定はこのブラウザーに保存されます。位置情報や IP は取得しません。','年を省略：カーソルを合わせると完全な日付を表示します。','保存できません。設定はブラウザーを閉じるまで有効です。']
};
function cgST(key){return (CG_SETTING_TEXT[cgLanguage]||CG_SETTING_TEXT.en)[CG_SETTING_KEYS.indexOf(key)]||key;}
function cgBrowserLocale(){for(const value of [...(navigator.languages||[]),navigator.language,'en-US']){try{if(value)return new Intl.DateTimeFormat(value).resolvedOptions().locale;}catch{}}return 'en-US';}
const cgDefaults=()=>({dateFormat:'auto',region:cgBrowserLocale(),start:'overview',group:'customer',density:'comfortable',description:true,risk:true});
function cgReadSettings(){const defaults=cgDefaults();try{const v=JSON.parse(localStorage.getItem('cg_settings_v1')||'{}');if(!v||typeof v!=='object')return defaults;
 for(const [key,allowed] of Object.entries({dateFormat:['auto','dmy','short','mdy','slash','iso','text'],start:['overview','invoices','insights'],group:['customer','status','month','risk'],density:['comfortable','compact']})){if(allowed.includes(v[key]))defaults[key]=v[key];}
 if(typeof v.region==='string'){try{defaults.region=new Intl.DateTimeFormat(v.region).resolvedOptions().locale;}catch{}}
 for(const key of ['description','risk'])if(typeof v[key]==='boolean')defaults[key]=v[key];return defaults;
 }catch{return defaults;}}
let cgSettings=cgReadSettings(),cgStorageOK=true;
function cgSaveSettings(){try{localStorage.setItem('cg_settings_v1',JSON.stringify(cgSettings));cgStorageOK=true;}catch{cgStorageOK=false;}}
function cgParsedDate(input){const m=/^(\d{4})-(\d{2})-(\d{2})$/.exec(String(input||'').slice(0,10));if(!m)return null;const d=new Date(Date.UTC(+m[1],+m[2]-1,+m[3]));return d.getUTCFullYear()===+m[1]&&d.getUTCMonth()===+m[2]-1&&d.getUTCDate()===+m[3]?{m,d}:null;}
cgDate=function(input){const parsed=cgParsedDate(input);if(!parsed)return '—';const {m,d}=parsed,[,y,month,day]=m;
 switch(cgSettings.dateFormat){case 'dmy':return `${day}.${month}.${y}`;case 'short':return `${day}.${month}.`;case 'mdy':return `${month}/${day}/${y}`;case 'slash':return `${day}/${month}/${y}`;case 'iso':return `${y}-${month}-${day}`;case 'text':return new Intl.DateTimeFormat(CG_LOCALES[cgLanguage],{day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}).format(d);default:return new Intl.DateTimeFormat(cgSettings.region,{day:'2-digit',month:'2-digit',year:'numeric',timeZone:'UTC'}).format(d);}
};
function cgFullDate(input){const p=cgParsedDate(input);return p?new Intl.DateTimeFormat(cgSettings.region,{dateStyle:'full',timeZone:'UTC'}).format(p.d):'—';}
function cgApplyPreferences(){document.body.classList.toggle('compact-rows',cgSettings.density==='compact');document.body.classList.toggle('hide-description',!cgSettings.description);document.body.classList.toggle('hide-risk',!cgSettings.risk);}
function cgRenderSettings(){
 document.querySelectorAll('[data-settingtext]').forEach(el=>el.textContent=cgST(el.dataset.settingtext));
 const language=document.getElementById('settingLanguage');language.replaceChildren(...Object.entries(CG_LANGUAGES).sort((a,b)=>a[1].name.localeCompare(b[1].name,'de')).map(([code,info])=>new Option(info.name,code)));language.value=cgLanguage;
 for(const key of ['dateFormat','start','group','density'])document.getElementById('setting-'+key).value=cgSettings[key];
 for(const key of ['description','risk'])document.getElementById('setting-'+key).checked=cgSettings[key];
 document.getElementById('settingRegion').textContent=cgSettings.region;
 document.getElementById('settingPreview').textContent=cgDate('2026-10-26');
 document.getElementById('settingStatus').textContent=cgST(cgStorageOK?'saved':'storageError');
}
function cgSettingsRoute(){const settings=location.hash==='#settings';document.getElementById('settingsPanel').hidden=!settings;document.getElementById('dashboard').hidden=settings;document.querySelectorAll('.nav-item').forEach(el=>{const active=el.hash===(location.hash||'#overview');el.classList.toggle('selected',active);if(active)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});}
window.addEventListener('DOMContentLoaded',()=>{
 cgSaveSettings();cgApplyPreferences();cgRenderSettings();cgSettingsRoute();
 document.getElementById('settingsForm').addEventListener('change',e=>{const key=e.target.dataset.preference;if(!key)return;cgSettings[key]=e.target.type==='checkbox'?e.target.checked:e.target.value;cgSaveSettings();cgApplyPreferences();
  if(key==='group'){cgGroupBy=cgSettings.group;cgActiveGroup=null;}
  if(report){renderAnalytics();renderGrid();}cgRenderSettings();
 });
 document.getElementById('settingLanguage').addEventListener('change',e=>cgSelectLanguage(e.target.value));
 document.getElementById('settingsReset').onclick=()=>{cgSettings=cgDefaults();cgSaveSettings();cgGroupBy=cgSettings.group;cgChartCurrency='';cgActiveGroup=null;cgActiveMonth=null;cgApplyPreferences();cgSelectLanguage(cgDetectedLanguage());cgRenderSettings();};
 window.addEventListener('hashchange',cgSettingsRoute);
});
