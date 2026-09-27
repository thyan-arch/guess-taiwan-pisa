(function(){
"use strict";
/* 配色一律跟隨系統（見 _style.css 的 prefers-color-scheme） */
var D=JSON.parse(document.getElementById('pisa-data').textContent);
var board=document.getElementById('board');
var elTabs=document.getElementById('tabs'),elPager=document.getElementById('pager');
var CH=[['成績','我們很會考試嗎'],['自信','我覺得我做得到嗎'],['動機','我想學嗎'],
        ['性別','男生女生誰領先'],['城鄉','在哪裡出生決定多少'],['課堂','教室裡發生什麼事'],
        ['趨勢','十九年下來變了什麼']];
var seen={}, openId=null, tab='成績';   /* seen：看過的題目 id → 1 */
var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;

try{var raw=localStorage.getItem('pisa-tw-seen');if(raw)seen=JSON.parse(raw)||{};}catch(e){seen={};}
try{var tb=localStorage.getItem('pisa-tw-tab');
  if(tb&&CH.some(function(c){return c[0]===tb;}))tab=tb;}catch(e){}
function saveTab(){try{localStorage.setItem('pisa-tw-tab',tab);}catch(e){}}
function save(){try{localStorage.setItem('pisa-tw-seen',JSON.stringify(seen));}catch(e){}}
/* 流量統計：有載入 Google Analytics（make_site.py 的 GA_ID）才送事件，否則不做任何事 */
function track(name,params){try{if(typeof window.gtag==='function')window.gtag('event',name,params);}catch(e){}}

function fmt(spec,v){
  var m=/\{v:([+]?)\.(\d)f\}/.exec(spec);
  if(!m)return spec.replace('{v}',v);
  var s=v.toFixed(+m[2]);
  if(m[1]==='+'&&v>0)s='+'+s;
  return spec.replace(m[0],s);
}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){
  return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function stars(s){if(s==null)return'';var n=s>=45?3:(s>=20?2:1);
  return '<span class="stars" title="意外指數（由資料計算）">'+'★'.repeat(n)+'☆'.repeat(3-n)+'</span>';}

/* ---------- 各分類已看題數 ---------- */
function chapterStat(name){
  var items=D.filter(function(d){return d.group===name;});
  var done=items.filter(function(d){return seen[d.id];}).length;
  return {done:done,total:items.length,all:items.length>0&&done===items.length};
}
function renderTabs(){
  elTabs.innerHTML=CH.map(function(c){
    var st=chapterStat(c[0]);
    return '<button class="tab" type="button" data-tab="'+esc(c[0])+'" aria-current="'+(tab===c[0])+'">'
      +(st.all?'<span class="dot" aria-hidden="true"></span>':'')+esc(c[0])
      +'<span class="tn">'+st.done+'/'+st.total+'</span></button>';
  }).join('');
}
function renderPager(){
  var i=CH.findIndex(function(c){return c[0]===tab;});
  var prev=i>0?CH[i-1][0]:null, next=i<CH.length-1?CH[i+1][0]:null;
  elPager.innerHTML=(prev?'<button class="btn alt" data-tab="'+esc(prev)+'" type="button">← '+esc(prev)+'</button>':'')
    +'<span class="sp"></span>'
    +(next?'<button class="btn" data-tab="'+esc(next)+'" type="button">'+esc(next)+' →</button>':'');
}

/* ---------- 圖表寬度：依卡片實際寬度畫，手機上字級不會被縮小 ---------- */
function chartW(){return Math.max(240,Math.min(760,Math.round(board.clientWidth-34)));}
/* 估算 12px 標籤的寬度（中文字約 12px、數字與符號約 7px），用來決定圖表左右留白 */
function textW(t){var w=0;for(var i=0;i<t.length;i++)w+=/[\u2E80-\uFFFF]/.test(t[i])?12:7;return w;}

/* ---------- 圖表：一般題（各國由低到高排成光譜） ---------- */
function chartRank(d){
  var W=chartW(),nar=W<520,H=nar?260:300,L=nar?48:56,R=nar?16:104,T=52,B=40,n=d.n,vals=d.dist;
  var lo=Math.min.apply(null,vals),hi=Math.max.apply(null,vals);
  if(d.oecd!=null){lo=Math.min(lo,d.oecd);hi=Math.max(hi,d.oecd);}
  var pad=(hi-lo)*0.12||1,LO=lo-pad,HI=hi+pad;
  L=Math.max(L,Math.max(textW(fmt(d.fmt,hi)),textW(fmt(d.fmt,lo)))+14);
  if(!nar&&d.oecd!=null)R=Math.max(R,textW('OECD '+fmt(d.fmt,d.oecd))+16);
  function X(p){return L+p/100*(W-L-R);}
  function Y(v){return T+(HI-v)/(HI-LO)*(H-T-B);}
  var pts=vals.map(function(v,k){return X(100*k/Math.max(1,n-1)).toFixed(1)+','+Y(v).toFixed(1);}).join(' ');
  var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="'+esc(d.label)
    +'：'+n+' 個國家或經濟體由「'+esc(d.poles[0])+'」排到「'+esc(d.poles[1])+'」，臺灣落在'+esc(zone(d,d.pos))+'">';
  s+='<polyline points="'+X(0).toFixed(1)+','+(H-B)+' '+pts+' '+X(100).toFixed(1)+','+(H-B)
    +'" fill="var(--blue-50)"/>';
  s+='<polyline points="'+pts+'" fill="none" stroke="var(--blue-300)" stroke-width="2"/>';
  if(d.oecd!=null){var oy=Y(d.oecd);
    s+='<line x1="'+L+'" y1="'+oy.toFixed(1)+'" x2="'+(W-R)+'" y2="'+oy.toFixed(1)
      +'" stroke="var(--ink-3)" stroke-width="1" stroke-dasharray="4 4"/>';
    s+=nar?'<text x="'+(L+4)+'" y="'+(oy-5).toFixed(1)+'" font-size="12" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">OECD '+esc(fmt(d.fmt,d.oecd))+'</text>'
      :'<text x="'+(W-R+8)+'" y="'+(oy+4).toFixed(1)+'" font-size="12" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">OECD '+esc(fmt(d.fmt,d.oecd))+'</text>';}
  var placed=[];
  d.marks.slice().sort(function(a,b){return a.p-b.p;}).forEach(function(m){
    var x=X(m.p),y=Y(m.v),w=m.zh.length*12+12,row=0;
    while(placed.some(function(p){return p.row===row&&Math.abs(p.x-x)<(p.w+w)/2;}))row++;
    placed.push({x:x,w:w,row:row});
    var ly=y-12-row*16,below=false;
    if(ly<T+12){ly=y+20+row*16;below=true;}
    var a=x<L+w/2?'start':(x>W-R-w/2?'end':'middle');
    s+='<line x1="'+x.toFixed(1)+'" y1="'+(y+(below?6:-6)).toFixed(1)+'" x2="'+x.toFixed(1)
      +'" y2="'+(below?ly-11:ly+4).toFixed(1)+'" stroke="var(--teal-300)"/>';
    s+='<circle cx="'+x.toFixed(1)+'" cy="'+y.toFixed(1)+'" r="4" fill="var(--teal-500)"/>';
    s+='<text x="'+x.toFixed(1)+'" y="'+ly.toFixed(1)+'" font-size="12" text-anchor="'+a
      +'" fill="var(--accent-ink)" font-family="Noto Sans TC,sans-serif">'+esc(m.zh)+'</text>';
  });
  var tx=X(d.pos),ty=Y(d.tw);
  s+='<g class="'+(reduce?'':'pop')+'" style="transform-origin:'+tx.toFixed(1)+'px '+ty.toFixed(1)+'px">';
  s+='<line x1="'+tx.toFixed(1)+'" y1="'+(T-20)+'" x2="'+tx.toFixed(1)+'" y2="'+(H-B)+'" stroke="var(--yel-500)" stroke-width="2"/>';
  s+='<circle cx="'+tx.toFixed(1)+'" cy="'+ty.toFixed(1)+'" r="7" fill="var(--yel-500)" stroke="var(--surface)" stroke-width="2"/>';
  var an=d.pos>70?'end':(d.pos<16?'start':'middle');
  s+='<text x="'+tx.toFixed(1)+'" y="'+(T-26)+'" font-size="14" font-weight="700" text-anchor="'+an
    +'" fill="var(--yel-700)" font-family="Noto Sans TC,sans-serif">臺灣</text></g>';
  s+='<line x1="'+L+'" y1="'+(H-B)+'" x2="'+(W-R)+'" y2="'+(H-B)+'" stroke="var(--line)"/>';
  var eL=endLabels(d);
  s+='<text x="'+L+'" y="'+(H-B+32)+'" font-size="13" font-weight="700" fill="var(--ink-2)" font-family="Noto Sans TC,sans-serif">'+esc(eL[0])+'</text>';
  s+='<text x="'+(W-R)+'" y="'+(H-B+32)+'" font-size="13" font-weight="700" text-anchor="end" fill="var(--ink-2)" font-family="Noto Sans TC,sans-serif">'+esc(eL[1])+'</text>';
  s+='<text x="'+(L-8)+'" y="'+(T+4)+'" font-size="12" text-anchor="end" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">'+esc(fmt(d.fmt,hi))+'</text>';
  s+='<text x="'+(L-8)+'" y="'+(H-B)+'" font-size="12" text-anchor="end" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">'+esc(fmt(d.fmt,lo))+'</text>';
  return s+'</svg>';
}

/* ---------- 圖表：趨勢題（跨屆折線） ---------- */
function chartTrend(d){
  var W=chartW(),nar=W<520,H=nar?280:330,L=nar?56:66,R=nar?56:96,T=56,B=52,cy=d.cycles,n=cy.length;
  var all=[];
  d.tw.forEach(function(v){if(v!=null)all.push(v);});
  if(d.oecd)d.oecd.forEach(function(v){if(v!=null)all.push(v);});
  d.refs.forEach(function(r){r.v.forEach(function(v){if(v!=null)all.push(v);});});
  var lo=Math.min.apply(null,all),hi=Math.max.apply(null,all);
  var pad=(hi-lo)*0.14||1,LO=lo-pad,HI=hi+pad;
  L=Math.max(L,Math.max(textW(fmt(d.fmt,HI-pad/2)),textW(fmt(d.fmt,LO+pad/2)))+14);
  function X(i){return L+i/(n-1)*(W-L-R);}
  function Y(v){return T+(HI-v)/(HI-LO)*(H-T-B);}
  function path(arr){var out=[],started=false;
    arr.forEach(function(v,i){if(v==null)return;out.push((started?'L':'M')+X(i).toFixed(1)+' '+Y(v).toFixed(1));started=true;});
    return out.join(' ');}
  var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="'+esc(d.label)+'：臺灣跨屆變化">';
  cy.forEach(function(y,i){
    s+='<line x1="'+X(i).toFixed(1)+'" y1="'+T+'" x2="'+X(i).toFixed(1)+'" y2="'+(H-B)+'" stroke="var(--line)" stroke-dasharray="2 4"/>';
    s+='<text x="'+X(i).toFixed(1)+'" y="'+(H-B+20)+'" font-size="12" text-anchor="middle" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">'+y+'</text>';
  });
  if(d.oecd){
    s+='<path d="'+path(d.oecd)+'" fill="none" stroke="var(--ink-3)" stroke-width="1.5" stroke-dasharray="5 4"/>';
    var lastO=null;d.oecd.forEach(function(v,i){if(v!=null)lastO=i;});
    if(lastO!=null)s+='<text x="'+(X(lastO)+8)+'" y="'+(Y(d.oecd[lastO])+4).toFixed(1)+'" font-size="12" fill="var(--ink-3)" font-family="Noto Sans TC,sans-serif">OECD</text>';
  }
  var rows=[];
  d.refs.forEach(function(r){
    s+='<path d="'+path(r.v)+'" fill="none" stroke="var(--teal-300)" stroke-width="1.5" opacity=".85"/>';
    var last=null;r.v.forEach(function(v,i){if(v!=null)last=i;});
    if(last!=null)rows.push({y:Y(r.v[last]),x:X(last),zh:r.zh});
  });
  rows.sort(function(a,b){return a.y-b.y;});
  var prev=-99;
  rows.forEach(function(r){var yy=Math.max(r.y,prev+14);prev=yy;
    s+='<text x="'+(r.x+8)+'" y="'+(yy+4).toFixed(1)+'" font-size="12" fill="var(--accent-ink)" font-family="Noto Sans TC,sans-serif">'+esc(r.zh)+'</text>';});
  s+='<path d="'+path(d.tw)+'" fill="none" stroke="var(--yel-500)" stroke-width="3"/>';
  d.tw.forEach(function(v,i){
    if(v==null)return;
    var isLast=i===d.guess_i;
    s+='<circle cx="'+X(i).toFixed(1)+'" cy="'+Y(v).toFixed(1)+'" r="'+(isLast?7:4.5)
      +'" fill="var(--yel-500)" stroke="var(--surface)" stroke-width="2"'+(isLast&&!reduce?' class="pop"':'')+'/>';
  });
  s+='<text x="'+X(0).toFixed(1)+'" y="'+(Y(d.tw[0])+22).toFixed(1)+'" font-size="13" font-weight="700" fill="var(--yel-700)" font-family="Noto Sans TC,sans-serif">臺灣</text>';
  s+='<line x1="'+L+'" y1="'+(H-B)+'" x2="'+(W-R)+'" y2="'+(H-B)+'" stroke="var(--line)"/>';
  s+='<text x="'+(L-8)+'" y="'+(T+4)+'" font-size="12" text-anchor="end" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">'+esc(fmt(d.fmt,HI-pad/2))+'</text>';
  s+='<text x="'+(L-8)+'" y="'+(H-B)+'" font-size="12" text-anchor="end" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">'+esc(fmt(d.fmt,LO+pad/2))+'</text>';
  return s+'</svg>';
}


/* ---------- 光譜位置 / 定位語 ---------- */
function diffUnit(d){return {pct:' 個百分點',score:' 分',points10:' 分'}[d.kind]||'';}
function lowBetter(d){return d.hib===false;}
/* 光譜位置 0–100（左＝數值低，右＝數值高）翻成文字 */
function zone(d,p){
  if(p==null)return '—';
  var lo=d.poles[0],hi=d.poles[1];
  if(p>=80)return hi+'的那一端';
  if(p>=60)return '偏'+hi;
  if(p>40)return '中間';
  if(p>20)return '偏'+lo;
  return lo+'的那一端';
}
function endLabels(d){return ['← '+d.poles[0],d.poles[1]+' →'];}
function verdictWord(d){
  if(d.neutral)return null;
  var q=lowBetter(d)?100-d.pos:d.pos;
  return q>=75?['臺灣的強項','v0']:(q<=30?['臺灣的弱項','v3']:['不算強也不算弱','v2']);
}
/* 一句話定位：數值跟 OECD 比，再說明落在光譜哪裡、跟哪些國家相比 */
function placement(d){
  var parts=[];
  if(d.oecd!=null){
    var diff=d.tw-d.oecd, ab=Math.abs(diff);
    var m=/\{v:[+]?\.(\d)f\}/.exec(d.fmt), dec=m?+m[1]:1;
    parts.push('臺灣 '+fmt(d.fmt,d.tw)+'，OECD 平均 '+fmt(d.fmt,d.oecd)
      +'（'+(diff>=0?'高':'低')+' '+ab.toFixed(dec)+diffUnit(d)+'）');
  }else{
    parts.push('臺灣 '+fmt(d.fmt,d.tw));
  }
  parts.push('在 '+d.n+' 個國家／經濟體排成的光譜上，臺灣落在「'+zone(d,d.pos)+'」');
  var hiSide=d.marks.filter(function(x){return x.p>d.pos;}).map(function(x){return x.zh;}),
      loSide=d.marks.filter(function(x){return x.p<d.pos;}).map(function(x){return x.zh;});
  var cmp=[];
  if(hiSide.length)cmp.push(hiSide.join('、')+'比臺灣更靠近「'+d.poles[1]+'」');
  if(loSide.length)cmp.push(loSide.join('、')+'比臺灣更靠近「'+d.poles[0]+'」');
  if(cmp.length)parts.push(cmp.join('；'));
  return parts.join('。')+'。';
}
function trendPlacement(d){
  var i=d.guess_i, v=d.tw[i], v0=d.tw[0];
  var m=/\{v:[+]?\.(\d)f\}/.exec(d.fmt), dec=m?+m[1]:1;
  var out=[];
  if(v0!=null){
    var diff=v-v0;
    out.push(d.cycles[0]+' 年到 '+d.cycles[i]+' 年，從 '+fmt(d.fmt,v0)+'變成 '+fmt(d.fmt,v)
      +'（'+(diff>=0?'增加':'減少')+' '+Math.abs(diff).toFixed(dec)+diffUnit(d)+'）');
  }
  var z0=zone(d,d.pos[0]), zN=zone(d,d.pos[i]);
  if(d.pos[0]!=null&&d.pos[i]!=null)
    out.push(z0===zN?'放到各國之中看，兩個年度都落在「'+zN+'」'
      :'放到各國之中看，從「'+z0+'」移到「'+zN+'」');
  if(d.oecd&&d.oecd[i]!=null)
    out.push('同一年 OECD 平均是 '+fmt(d.fmt,d.oecd[i]));
  return out.join('。')+'。';
}

/* ---------- 卡片 ---------- */
function unitHelp(d){
  if(/\{v:[+]?\.2f\}/.test(d.fmt)&&d.kind!=='points10')
    return '這是一個「指數」：OECD 平均 = 0，正數代表高於國際平均，1.0 大約等於一個標準差。';
  return '';
}
function face(d){
  return '<h4>'+esc(d.teaser)+'</h4><p class="hook">'+esc(d.hook)+'</p>'
    +'<div class="foot">'+(seen[d.id]?'<span class="badge">已看過</span>':'')
    +'<span class="badge cyc">'+(d.type==='trend'
      ?(d.cycles[0]+'→'+d.cycles[d.cycles.length-1]):('PISA '+d.cycle))+'</span>'+stars(d.surprise)+'</div>';
}
function detailUI(d){
  var help=unitHelp(d);
  var vw=d.type==='trend'?null:verdictWord(d);
  var place=d.type==='trend'?trendPlacement(d):placement(d);
  var big,tbl;
  if(d.type==='trend'){
    big=esc(fmt(d.fmt,d.tw[d.guess_i]))+' <small>'+d.cycles[d.guess_i]+' 年</small>';
    var head='<tr><th>國家／經濟體</th>'+d.cycles.map(function(y){return '<th>'+y+'</th>';}).join('')+'</tr>';
    var body='<tr class="tw"><td>臺灣</td>'+d.tw.map(function(v){return '<td>'+(v==null?'—':esc(fmt(d.fmt,v)))+'</td>';}).join('')+'</tr>';
    body+='<tr class="tw"><td>臺灣在各國中的位置</td>'+d.pos.map(function(p){return '<td>'+esc(zone(d,p))+'</td>';}).join('')+'</tr>';
    if(d.oecd)body+='<tr class="oecd"><td>OECD 平均</td>'+d.oecd.map(function(v){return '<td>'+(v==null?'—':esc(fmt(d.fmt,v)))+'</td>';}).join('')+'</tr>';
    d.refs.forEach(function(r){body+='<tr><td>'+esc(r.zh)+'</td>'+r.v.map(function(v){return '<td>'+(v==null?'—':esc(fmt(d.fmt,v)))+'</td>';}).join('')+'</tr>';});
    tbl='<div class="tblwrap"><table><caption>'+esc(d.label)+'</caption><thead>'+head+'</thead><tbody>'+body+'</tbody></table></div>';
  }else{
    big=esc(zone(d,d.pos));
    var rows='<tr class="tw"><td>臺灣</td><td>'+esc(fmt(d.fmt,d.tw))+'</td><td>'+esc(zone(d,d.pos))+'</td></tr>';
    if(d.oecd!=null)rows+='<tr class="oecd"><td>OECD 平均</td><td>'+esc(fmt(d.fmt,d.oecd))+'</td><td>—</td></tr>';
    d.marks.forEach(function(m){rows+='<tr><td>'+esc(m.zh)+'</td><td>'+esc(fmt(d.fmt,m.v))+'</td><td>'+esc(zone(d,m.p))+'</td></tr>';});
    rows+='<tr class="oecd"><td>最右端（'+esc(d.poles[1])+'）｜ '+esc(d.top.zh)+'</td><td>'+esc(fmt(d.fmt,d.top.v))+'</td><td>—</td></tr>';
    rows+='<tr class="oecd"><td>最左端（'+esc(d.poles[0])+'）｜ '+esc(d.bottom.zh)+'</td><td>'+esc(fmt(d.fmt,d.bottom.v))+'</td><td>—</td></tr>';
    tbl='<div class="tblwrap"><table><caption>'+esc(d.label)+'（PISA '+d.cycle+'）</caption>'
      +'<thead><tr><th>國家／經濟體</th><th>數值</th><th>在光譜上的位置</th></tr></thead><tbody>'+rows+'</tbody></table></div>';
  }
  return '<div class="detail"><p class="q">'+esc(d.q)+'</p>'
    +'<p class="what">'+esc(d.what)+(help?' '+help:'')+'</p>'
    +'<div class="judge"><span class="big">'+big+'</span>'
    +(vw?'<span class="verdict '+vw[1]+'">'+esc(vw[0])+'</span>':'')+'</div>'
    +'<p class="place">'+esc(place)+'</p>'
    +'<div class="chartwrap">'+(d.type==='trend'?chartTrend(d):chartRank(d))+'</div>'
    +tbl+'<p class="insight">'+esc(d.note)+'</p>'
    +'<p class="src">資料表：'+esc(d.src)+'</p>'
    +'<div class="acts"><button class="btn alt" data-act="close" type="button">收起</button></div></div>';
}

function render(){
  renderTabs();renderPager();
  var c=CH.filter(function(x){return x[0]===tab;})[0]||CH[0];
  var items=D.filter(function(d){return d.group===c[0];});
  var st=chapterStat(c[0]);
  var html='<section class="chapter"><div class="chapter-h"><i></i><h3>'+esc(c[0])+'</h3><em>'
    +esc(c[1])+'</em><span class="cs">'+st.done+' / '+st.total+' 已看</span></div><div class="grid">';
  items.forEach(function(d){
    var open=openId===d.id,tag=open?'div':'button';
    html+='<'+tag+' class="qcard'+(open?' open':'')+'" '+(open?'':'type="button" ')
      +'data-card="'+d.id+'">'+face(d)+(open?detailUI(d):'')+'</'+tag+'>';
  });
  html+='</div></section>';
  board.innerHTML=html;
}

function goTab(name){
  if(tab===name)return;
  tab=name;openId=null;saveTab();render();
  track('view_tab',{tab_name:name});
  var top=elTabs.getBoundingClientRect().top+window.scrollY-8;
  window.scrollTo({top:Math.max(0,top),behavior:reduce?'auto':'smooth'});
}
elTabs.addEventListener('click',function(ev){
  var b=ev.target.closest('[data-tab]');if(b)goTab(b.getAttribute('data-tab'));});
elPager.addEventListener('click',function(ev){
  var b=ev.target.closest('[data-tab]');if(b)goTab(b.getAttribute('data-tab'));});

board.addEventListener('click',function(ev){
  if(ev.target.closest('[data-act="close"]')){openId=null;render();return;}
  var card=ev.target.closest('[data-card]');
  if(card&&card.tagName==='BUTTON'){
    openId=card.getAttribute('data-card');seen[openId]=1;save();render();
    var dd=D.filter(function(x){return x.id===openId;})[0];
    if(dd)track('open_card',{card_id:dd.id,card_title:dd.teaser,card_group:dd.group});
    var el=document.querySelector('[data-card="'+openId+'"]');
    if(el)el.scrollIntoView({behavior:reduce?'auto':'smooth',block:'start'});
  }
});

/* 螢幕寬度改變（例如手機轉向）時，重畫已展開的圖表 */
var lastW=chartW(),rt=null;
window.addEventListener('resize',function(){
  clearTimeout(rt);rt=setTimeout(function(){
    var w=chartW();if(w!==lastW){lastW=w;if(openId)render();}},200);});

render();
})();
