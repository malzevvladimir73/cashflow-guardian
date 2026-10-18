
/* Cashflow Guardian — localized interface and grounded invoice explanations. */
'use strict';
let source='demo';
let report=null;
let gridApi=null;
const $=id=>document.getElementById(id);
const money=(currency,val)=>cgMoney(currency,val);
const safe=s=>String(s??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
const OPEN_STATES=['SENT','UNPAID','PARTIALLY_PAID','PAYMENT_PENDING','OVERDUE'];

function toast(message,isError=false){
 const el=$('message');el.hidden=false;el.textContent=message;
 el.style.background=isError?'#fff0e9':'#eafbf5';el.style.color=isError?'#a25432':'#2b796b';
}
function hideToast(){$('message').hidden=true;}
async function api(path,options={}){
 if(window.CG_OFFLINE_REPORT){
  if(path==='/api/status')return {sandbox_configured:false};
  if(path.startsWith('/api/analyze?')){
   if(path.includes('sandbox'))throw new Error(cgT('sandboxDisabled'));
   return window.CG_OFFLINE_REPORT;
  }
  throw new Error(cgT('genericError'));
 }
 const response=await fetch(path,options);
 let data;try{data=await response.json();}catch{throw new Error(cgT('genericError'));}
 if(!response.ok)throw new Error(data.error||`HTTP ${response.status}`);
 return data;
}

/* Invoice visual analytics. Currency segments are NEVER added together. */
let cgGroupBy='customer',cgChartCurrency='',cgActiveGroup=null,cgActiveMonth=null;
function cgGroupKey(row,by=cgGroupBy){
 if(by==='customer')return String(row.customer||'—');
 if(by==='status')return String(row.status||'—');
 if(by==='risk')return String(row.risk||'Low');
 return /^\d{4}-\d{2}/.test(String(row.due||''))?String(row.due).slice(0,7):'—';
}
function cgGroupName(key,by=cgGroupBy){
 if(key==='—')return cgT('unassigned');
 if(by==='status'||by==='risk')return cgStatus(key);
 if(by==='month'&&/^\d{4}-\d{2}$/.test(key)){
  const d=new Date(key+'-01T12:00:00');
  return new Intl.DateTimeFormat(CG_LOCALES[cgLanguage],{month:'long',year:'numeric'}).format(d);
 }
 return key;
}
function cgAmounts(row){
 const amount=Math.max(0,Number(row.amount)||0);
 const raw=row.due_amount;
 const due=raw===null||raw===undefined||raw===''?amount:Number(raw);
 const open=OPEN_STATES.includes(row.status)?Math.min(amount,Math.max(0,Number.isFinite(due)?due:amount)):0;
 const paid=row.status==='PAID'?amount:row.status==='PARTIALLY_PAID'?amount-open:0;
 return {open,paid};
}
function cgRowValue(row){const v=cgAmounts(row);return row.status==='PAID'?v.paid:v.open;}
function cgGroupMatch(row){
 return row.currency===cgChartCurrency&&(!cgActiveGroup||cgGroupKey(row,cgActiveGroup.by)===cgActiveGroup.key)&&(!cgActiveMonth||cgGroupKey(row,'month')===cgActiveMonth);
}
function cgSearchMatch(row){
 const x=visibleRow(row),q=$('filter').value.trim().toLocaleLowerCase(CG_LOCALES[cgLanguage]);
 return [x.number,x.customer,x.description,x.statusText,x.riskText,x.flagsText].join(' ').toLocaleLowerCase(CG_LOCALES[cgLanguage]).includes(q);
}
function cgVisibleRows(){return report.invoices.filter(cgGroupMatch).filter(cgSearchMatch);}
function cgChangeGroup(key){
 if(cgActiveGroup&&cgActiveGroup.key===key&&cgActiveGroup.by===cgGroupBy&&cgActiveGroup.currency===cgChartCurrency){cgActiveGroup=null;}
 else cgActiveGroup={key,by:cgGroupBy,currency:cgChartCurrency};
 renderAnalytics();renderGrid();
 document.getElementById('invoices')?.scrollIntoView({block:'start',behavior:'smooth'});
}
function renderAnalytics(){
 if(!report)return;
 const rows=report.invoices||[];
 const options=[...new Set(rows.map(x=>x.currency||'USD'))].sort();
 const currencySelect=$('chartCurrency');
 if(!options.includes(cgChartCurrency))cgChartCurrency=options[0]||'USD';
 const was=currencySelect.value;
 currencySelect.replaceChildren(...options.map(c=>{const opt=document.createElement('option');opt.value=c;opt.textContent=c;return opt;}));
 currencySelect.value=cgChartCurrency;
 $('groupBy').value=cgGroupBy;
 const relevant=rows.filter(x=>x.currency===cgChartCurrency).filter(cgSearchMatch);
 const groups=new Map();
 for(const row of relevant){
  const key=cgGroupKey(row),value=cgRowValue(row);
  if(!groups.has(key))groups.set(key,{key,paid:0,open:0,n:0});
  const x=groups.get(key);x.n++;
  const amounts=cgAmounts(row);x.paid+=amounts.paid;x.open+=amounts.open;
 }
 const sorted=[...groups.values()].sort((a,b)=>cgGroupBy==='month'?a.key.localeCompare(b.key):(b.paid+b.open)-(a.paid+a.open)||a.key.localeCompare(b.key));
 const max=Math.max(1,...sorted.map(x=>x.paid+x.open));
 const chart=$('groupChart');chart.replaceChildren();
 if(!sorted.length){const msg=document.createElement('p');msg.className='no-chart-data';msg.textContent=cgT('emptyChart');chart.append(msg);}
 for(const item of sorted){
  const row=document.createElement('button');row.type='button';row.className='group-bar';
  row.setAttribute('aria-pressed',String(!!cgActiveGroup&&cgActiveGroup.by===cgGroupBy&&cgActiveGroup.key===item.key&&cgActiveGroup.currency===cgChartCurrency));
  const total=item.paid+item.open;
  const label=cgGroupName(item.key);
  row.setAttribute('aria-label',label+': '+money(cgChartCurrency,total)+', '+cgT('recordsGrouped',{n:item.n}));
  row.title=label+' · '+money(cgChartCurrency,total);
  const top=document.createElement('div');top.className='group-bar-top';
  const name=document.createElement('span');name.className='group-bar-name';name.textContent=label;name.title=label;
  const value=document.createElement('span');value.className='group-bar-value';value.textContent=money(cgChartCurrency,total);
  top.append(name,value);
  const track=document.createElement('div');track.className='bar-track';
  const open=document.createElement('span');open.className='bar-segment bar-open';open.style.width=100*item.open/max+'%';
  const paid=document.createElement('span');paid.className='bar-segment bar-paid';paid.style.width=100*item.paid/max+'%';
  track.append(open,paid);row.append(top,track);row.addEventListener('click',()=>cgChangeGroup(item.key));chart.append(row);
 }
 $('groupClear').hidden=!cgActiveGroup&&!cgActiveMonth&&!$('filter').value;
 if(cgActiveGroup)$('groupClear').title=cgT('groupSelected',{name:cgGroupName(cgActiveGroup.key,cgActiveGroup.by)});
 const today=new Date();today.setHours(0,0,0,0);
 let paid=0,overdue=0,upcoming=0;
 for(const row of relevant.filter(cgGroupMatch)){const amounts=cgAmounts(row);const v=amounts.open;paid+=amounts.paid;
 if(OPEN_STATES.includes(row.status)){
  const d=/^\d{4}-\d{2}-\d{2}$/.test(String(row.due||''))?new Date(row.due+'T00:00:00'):null;
  if((Number(row.days_overdue)||0)>0||(d&&d<today))overdue+=v;else upcoming+=v;
 }}
 const parts=[{key:'paidLegend',amount:paid,color:'#4c98ea'},{key:'overdueLegend',amount:overdue,color:'#ef9c67'},{key:'upcomingLegend',amount:upcoming,color:'#2cb597'}];
 const grand=paid+overdue+upcoming;
 const totalRing=2*Math.PI*76;
 const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 220 220');svg.setAttribute('role','img');
 svg.setAttribute('aria-label',cgT('distribution')+': '+parts.map(p=>cgT(p.key)+' '+money(cgChartCurrency,p.amount)).join(', '));
 const base=document.createElementNS('http://www.w3.org/2000/svg','circle');
 for(const [k,v] of Object.entries({cx:'110',cy:'110',r:'76',fill:'none',stroke:'#eaf1f6','stroke-width':'25'}))base.setAttribute(k,v);
 svg.append(base);let offset=0;
 for(const part of parts){if(!grand||!part.amount)continue;
  const circle=document.createElementNS('http://www.w3.org/2000/svg','circle');
  for(const [k,v] of Object.entries({cx:'110',cy:'110',r:'76',fill:'none',stroke:part.color,'stroke-width':'25',transform:'rotate(-90 110 110)','stroke-dasharray':`${(part.amount/grand)*totalRing} ${totalRing}`,'stroke-dashoffset':String(-offset*totalRing)}))circle.setAttribute(k,v);
  offset+=part.amount/grand;svg.append(circle);
 }
 const donut=$('donutChart');donut.replaceChildren(svg);
 const center=document.createElement('div');center.className='donut-center';const percent=document.createElement('strong');percent.textContent=grand?Math.round(100*paid/grand)+'%':'—';const sub=document.createElement('small');sub.textContent=cgT('paidLegend');center.append(percent,sub);donut.append(center);
 const legend=$('donutLegend');legend.replaceChildren();
 for(const part of parts){const el=document.createElement('div');el.className='donut-entry';const dot=document.createElement('i');dot.className='chart-dot';dot.style.background=part.color;const text=document.createElement('span');text.textContent=cgT(part.key);const sum=document.createElement('strong');sum.textContent=money(cgChartCurrency,part.amount);text.append(sum);el.append(dot,text);legend.append(el);}
}

function visibleRow(x){return {...x,description:cgDescription(x),statusText:cgStatus(x.status),riskText:cgStatus(x.risk),dueText:cgDate(x.due),issuedText:cgDate(x.issued),flagsText:cgFlags(x)};}
function renderSummary(){
 $('openCount').textContent=report.invoices.filter(x=>OPEN_STATES.includes(x.status)).length;
 const entries=Object.entries(report.summary.totals_by_currency||{});
 const show=key=>entries.length?entries.map(([cur,v])=>money(cur,v[key])).join(' + '):'—';
 $('outstanding').textContent=show('outstanding');$('overdue').textContent=show('overdue');
 $('flags').textContent=report.summary.flagged_count;
 $('connectionTitle').textContent=source==='demo'?cgT('synthetic'):'PayPal Sandbox';
 $('connectionText').textContent=cgT(source==='demo'?'syntheticDesc':'sandboxDesc');
 $('demoButton').classList.toggle('active',source==='demo');
 $('sandboxButton').classList.toggle('active',source==='sandbox');
}
function renderAlerts(){
 const rows=report.invoices.filter(x=>x.flags?.length)
   .sort((a,b)=>((b.risk==='High')-(a.risk==='High'))||(b.days_overdue-a.days_overdue)).slice(0,4);
 $('alerts').innerHTML=rows.length?rows.map(x=>{
  const duplicate=x.flags.some(v=>/duplicate/i.test(v));
  return `<div class="alert ${duplicate?'alert-duplicate':''}"><div class="alert-icon">${duplicate?'◇':'!'}</div><div><strong>${safe(x.customer)} <span style="color:#b0bfcc;font-weight:500">· ${safe(x.number)}</span></strong><p>${safe(cgFlags(x))}</p></div><span class="amount">${safe(money(x.currency,x.amount))}</span></div>`;
 }).join(''):`<div class="alert alert-nothing"><div class="alert-icon">✓</div><div><strong>${safe(cgT('allClear'))}</strong><p>${safe(cgT('noSignals'))}</p></div></div>`;
}
function columns(){return [
 {field:'number',headerName:cgT('invoice'),minWidth:122},
 {field:'customer',headerName:cgT('customer'),minWidth:154},
 {field:'description',headerName:cgT('details'),minWidth:200},
 {field:'amount',headerName:cgT('amount'),minWidth:125,valueFormatter:p=>money(p.data.currency,p.value)},
 {field:'statusText',headerName:cgT('status'),minWidth:125},
 {field:'dueText',headerName:cgT('dueDate'),minWidth:154},
 {field:'riskText',headerName:cgT('aiSignal'),minWidth:124}
];}
function gridStrings(){return {page:cgT('page'),next:cgT('next'),previous:cgT('previous'),of:cgT('of'),to:cgT('to'),pageSize:cgT('pageSize'),noRowsToShow:cgT('noRows'),filterOoo:cgT('filterOoo'),contains:cgT('contains'),notContains:cgT('notContains'),equals:cgT('equals'),blank:cgT('blank'),notBlank:cgT('notBlank'),loadingOoo:cgT('pleaseWait')};}
function renderGrid(){
 const rows=cgVisibleRows().map(visibleRow),oldFilter=$('filter').value;
 $('tableCount').textContent=cgT('records',{n:rows.length})+' · '+cgT(source==='demo'?'syntheticTag':'sandboxReadOnly');
 $('invoiceGrid').hidden=true;$('fallbackTable').hidden=false;
 const q=oldFilter.trim().toLocaleLowerCase(CG_LOCALES[cgLanguage]);
 const visible=rows.filter(x=>[x.number,x.customer,x.description,x.statusText,x.riskText,x.flagsText].join(' ').toLocaleLowerCase(CG_LOCALES[cgLanguage]).includes(q));
 visible.sort((a,b)=>{const av=a[cgSort.key]??'',bv=b[cgSort.key]??'';return (typeof av==='number'?av-bv:String(av).localeCompare(String(bv),CG_LOCALES[cgLanguage]))*cgSort.direction;});
 const headers=['invoice','issuedDate','customer','details','amount','status','dueDate','aiSignal'];
 const fields=['number','issued','customer','description','amount','statusText','due','riskText'];
 $('fallbackTable').innerHTML=`<div class="table-scroll"><table class="fallback"><thead><tr>${headers.map((h,i)=>`<th aria-sort="${cgSort.key===fields[i]?(cgSort.direction===1?'ascending':'descending'):'none'}"><button type="button" data-sort="${fields[i]}">${safe(cgT(h))} ${cgSort.key===fields[i]?(cgSort.direction===1?'↑':'↓'):''}</button></th>`).join('')}</tr></thead><tbody>`+
 (visible.length?visible.map(x=>`<tr><td>${safe(x.number)}</td><td class="date-cell">${safe(x.issuedText)}</td><td>${safe(x.customer)}</td><td>${safe(x.description)}</td><td class="num-cell">${safe(money(x.currency,x.amount))}</td><td>${safe(x.statusText)}</td><td class="date-cell">${safe(x.dueText)}</td><td>${safe(x.riskText)}</td></tr>`).join(''):`<tr><td colspan="8">${safe(cgT('noRows'))}</td></tr>`)+`</tbody></table></div>`;
}
let cgSort={key:'number',direction:1};
async function load(nextSource=source){
 hideToast();const previous=source;
 try{const data=await api('/api/analyze?source='+encodeURIComponent(nextSource));source=nextSource;report=data;cgActiveGroup=null;cgActiveMonth=null;renderSummary();renderAlerts();renderAnalytics();renderGrid();
   if(source==='sandbox')toast(cgT('sandboxLoaded'));
 }catch(e){source=previous;toast(nextSource==='sandbox'&&window.CG_OFFLINE_REPORT?cgT('sandboxDisabled'):e.message,true);}
}
function appendMessage(text,user=false){const el=document.createElement('div');el.className=user?'user-message':'bot-message';el.textContent=text;$('conversation').append(el);$('conversation').scrollTop=$('conversation').scrollHeight;}
function resetConversation(){$('conversation').replaceChildren();appendMessage(cgT('assistantWelcome'));}
function questionType(q){
 const text=String(q||'').toLocaleLowerCase();
 if(/\bINV-\d{3,}\b/i.test(q))return 'invoice';
 if(/dupl|dopp|dubl|dublet|podwójn|dublu|dubla|重复|重複|डुप्ल|تكرار|duplic|dédoubl|doppion/i.test(text))return 'duplicates';
 if(/überfällig|overdue|late|zaległ|przetermin|achterstall|verval|restant|scadenț|întârzi|vencid|retard|scadut|atrasad|逾期|अतिदेय|متأخر|期限超過|期限を過ぎ|支払期限/i.test(text))return 'overdue';
 if(/largest|highest|most|biggest|najwięks|hoogst|grootst|cel mai mare|größ|höchst|mayor|máxim|grande|maior|maggiore|massim|最大|सबसे|أكبر|最高/i.test(text))return 'largest';
 if(/urgent|attention|risk|prior|piln|ryzyk|dringend|risic|urgent|risc|dring|wichtig|risiko|riesgo|urgente|priorité|attenzion|urgência|紧急|優先|ज़रूरी|مهم|عاجل|リスク/i.test(text))return 'urgent';
 return 'help';
}
function answerLocal(q, forced){
 if(!report)return cgT('pleaseWait');
 const kind=forced||questionType(q),rows=report.invoices;
 if(kind==='invoice'){
  const number=(q.match(/INV-\d{3,}/i)||[])[0];const x=rows.find(x=>x.number?.toUpperCase()===number?.toUpperCase());
  return x?cgT('invoiceLead',{number:x.number,customer:x.customer,amount:money(x.currency,x.amount),status:cgStatus(x.status),due:cgDate(x.due),flags:cgFlags(x)||cgT('noSignals')}):cgT('unsupportedAsk');
 }
 if(kind==='duplicates'){
  const pairs=report.duplicates||[];
  return pairs.length?cgT('duplicateLead',{items:pairs.slice(0,6).map(x=>x.first+' + '+x.second+' ('+Math.round(x.similarity*100)+'%)').join('; ')}):cgT('noDuplicates');
 }
 if(kind==='overdue'){
  return cgT('overdueLead',{items:Object.entries(report.summary.totals_by_currency||{}).map(([c,v])=>money(c,v.overdue)).join(' · ')||'—'});
 }
 if(kind==='largest'){
  const items=rows.filter(x=>OPEN_STATES.includes(x.status)).sort((a,b)=>b.amount-a.amount).slice(0,3);
  return items.length?cgT('highestLead',{items:items.map(x=>x.number+' ('+x.customer+'): '+money(x.currency,x.due_amount??x.amount)).join('; ')}):cgT('noOpenInvoice');
 }
 if(kind==='urgent'){
  const items=rows.filter(x=>x.flags?.length).sort((a,b)=>((b.risk==='High')-(a.risk==='High'))||b.days_overdue-a.days_overdue).slice(0,5);
  return items.length?cgT('topRisk',{items:items.map(x=>x.number+' ('+x.customer+'): '+cgFlags(x)).join('; ')}):cgT('noFlags');
 }
 return cgT('unsupportedAsk');
}
function ask(q,intent){if(!q?.trim())return;appendMessage(q.trim(),true);$('question').value='';appendMessage(answerLocal(q.trim(),intent));}
function exportCSV(){
 if(!report)return;
 const cols=['number','customer','description','amount','currency','status','issued','due','risk','flags'];
 const names=['csv_number','csv_customer','csv_details','csv_amount','csv_currency','csv_status','csv_issued','csv_due','csv_risk','csv_flags'];
 const rows=cgVisibleRows().map(x=>({ ...x,description:cgDescription(x),status:cgStatus(x.status),risk:cgStatus(x.risk),flags:cgFlags(x)}));
 const quote=s=>{let text=String(s??'');if(/^[=+@\-\t\r]/.test(text))text="'"+text;return '"'+text.replaceAll('"','""')+'"';};
 const csv='\ufeff'+[names.map(k=>quote(cgT(k))).join(','),...rows.map(r=>cols.map(k=>quote(r[k])).join(','))].join('\r\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
 const a=document.createElement('a');a.href=url;a.download=`cashflow-guardian-${cgLanguage}-${source}-${new Date().toISOString().slice(0,10)}.csv`;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),300);
}
function cgOnLanguageChanged(){
 if(report){renderSummary();renderAlerts();renderAnalytics();renderGrid();}
 resetConversation();
 if(!$('message').hidden)hideToast();
}
window.addEventListener('DOMContentLoaded',async()=>{
 cgInitLanguage();resetConversation();
 $('demoButton').onclick=()=>load('demo');$('sandboxButton').onclick=()=>load('sandbox');
 $('chatForm').addEventListener('submit',e=>{e.preventDefault();ask($('question').value);});
 const ids=['urgent','duplicates','overdue'];
 document.querySelectorAll('[data-prompt]').forEach((b,i)=>{b.onclick=()=>ask(cgT(['promptUrgent','promptDuplicate','promptOverdue'][i]),ids[i]);});
 $('filter').addEventListener('input',()=>{renderAnalytics();renderGrid();});
 $('export').onclick=exportCSV;
 $('fallbackTable').addEventListener('click',e=>{const b=e.target.closest('[data-sort]');if(!b)return;cgSort={key:b.dataset.sort,direction:cgSort.key===b.dataset.sort?-cgSort.direction:1};renderGrid();$('fallbackTable').querySelector('[data-sort="'+cgSort.key+'"]')?.focus();});
  $('groupBy').addEventListener('change',e=>{cgGroupBy=e.target.value;cgActiveGroup=null;renderAnalytics();renderGrid();});
  $('chartCurrency').addEventListener('change',e=>{cgChartCurrency=e.target.value;cgActiveGroup=null;cgActiveMonth=null;renderAnalytics();renderGrid();});
  $('groupClear').addEventListener('click',()=>{cgActiveGroup=null;cgActiveMonth=null;$('filter').value='';renderAnalytics();renderGrid();});
 try{const status=await api('/api/status');if(!status.sandbox_configured){$('sandboxButton').title=cgT('sandboxDisabled');}}catch(e){toast(cgT('serverError',{msg:e.message}),true);}
 await load('demo');
});


function renderMonthly(){
 if(!report)return;
 const groups=new Map();
 for(const row of report.invoices.filter(x=>x.currency===cgChartCurrency).filter(cgSearchMatch)){
  if(cgActiveGroup&&cgGroupKey(row,cgActiveGroup.by)!==cgActiveGroup.key)continue;
  const month=cgGroupKey(row,'month'),v=cgAmounts(row);
  if(!groups.has(month))groups.set(month,{open:0,paid:0});
  groups.get(month).open+=v.open;groups.get(month).paid+=v.paid;
 }
 const max=Math.max(1,...[...groups.values()].flatMap(x=>[x.open,x.paid]));
 const host=$('monthlyChart');host.replaceChildren();
 for(const [month,v] of [...groups].sort((a,b)=>a[0].localeCompare(b[0]))){
  const b=document.createElement('button');b.type='button';b.className='month-column';b.setAttribute('aria-pressed',String(cgActiveMonth===month));
  const label=cgGroupName(month,'month');
  b.setAttribute('aria-label',label+', '+cgT('openLegend')+': '+money(cgChartCurrency,v.open)+', '+cgT('paidLegend')+': '+money(cgChartCurrency,v.paid));
  b.innerHTML=`<span>${safe(label)}</span><div class="month-bars"><i style="height:${v.open/max*100}%"></i><i style="height:${v.paid/max*100}%"></i></div><small>${safe(cgT('openLegend'))}: ${safe(money(cgChartCurrency,v.open))}</small><small>${safe(cgT('paidLegend'))}: ${safe(money(cgChartCurrency,v.paid))}</small>`;
  b.onclick=()=>{cgActiveMonth=cgActiveMonth===month?null:month;renderAnalytics();renderGrid();};host.append(b);
 }
 if(!groups.size)host.textContent=cgT('emptyChart');
}
const cgRenderAnalyticsBase=renderAnalytics;
renderAnalytics=function(){cgRenderAnalyticsBase();renderMonthly();};
