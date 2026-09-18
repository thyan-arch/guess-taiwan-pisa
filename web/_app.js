(function(){
"use strict";
/* ---------- 配色：跟隨系統 / 淺色 / 深色 ---------- */
var THEMES=[['auto','跟隨系統'],['light','淺色'],['dark','深色']],ti=0;
try{var tv=localStorage.getItem('pisa-tw-theme');
  for(var z=0;z<THEMES.length;z++)if(THEMES[z][0]===tv)ti=z;}catch(e){}
function applyTheme(){
  var m=THEMES[ti][0],r=document.documentElement;
  if(m==='auto')r.removeAttribute('data-theme');else r.setAttribute('data-theme',m);
  var b=document.getElementById('theme');
  if(b){b.textContent='配色：'+THEMES[ti][1];
    b.setAttribute('aria-label','切換配色，目前為'+THEMES[ti][1]);}
  try{localStorage.setItem('pisa-tw-theme',m);}catch(e){}
}
applyTheme();
document.getElementById('theme').addEventListener('click',function(){
  ti=(ti+1)%THEMES.length;applyTheme();});

var D=JSON.parse(document.getElementById('pisa-data').textContent);
var board=document.getElementById('board');
var elScore=document.getElementById('score'),elStreak=document.getElementById('streak'),
    elProg=document.getElementById('prog'),elCnt=document.getElementById('cnt'),
    elTabs=document.getElementById('tabs'),elPager=document.getElementById('pager');
var CH=[['成績','我們很會考試嗎'],['自信','我覺得我做得到嗎'],['動機','我想學嗎'],
        ['性別','男生女生誰領先'],['城鄉','在哪裡出生決定多少'],['課堂','教室裡發生什麼事'],
        ['趨勢','十九年下來變了什麼']];
var MAXPTS=1000, state={}, openId=null, justRevealed=null, tab='成績';
var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;

try{var raw=localStorage.getItem('pisa-tw-v2');if(raw)state=JSON.parse(raw)||{};}catch(e){state={};}
try{var tb=localStorage.getItem('pisa-tw-tab');
  if(tb&&(tb==='summary'||CH.some(function(c){return c[0]===tb;})))tab=tb;}catch(e){}
function saveTab(){try{localStorage.setItem('pisa-tw-tab',tab);}catch(e){}}
function save(){try{localStorage.setItem('pisa-tw-v2',JSON.stringify(state));}catch(e){}}

function fmt(spec,v){
  var m=/\{v:([+]?)\.(\d)f\}/.exec(spec);
  if(!m)return spec.replace('{v}',v);
  var s=v.toFixed(+m[2]);
  if(m[1]==='+'&&v>0)s='+'+s;
  return spec.replace(m[0],s);
}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){
  return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function byId(id){for(var k=0;k<D.length;k++)if(D[k].id===id)return D[k];return null;}
function stars(s){if(s==null)return'';var n=s>=45?3:(s>=20?2:1);
  return '<span class="stars" title="意外指數（由資料計算，非使用者統計）">'+'★'.repeat(n)+'☆'.repeat(3-n)+'</span>';}

/* ---------- 計分 ---------- */
function answerOf(d){return d.type==='trend'?d.tw[d.guess_i]:d.rank;}
function errOf(d,g){
  if(d.type==='trend'){var sp=d.rng[1]-d.rng[0];return Math.abs(g-answerOf(d))/sp;}
  return Math.abs(g-d.rank)/Math.max(1,d.n-1);
}
function pointsOf(e){var x=Math.max(0,1-e/0.40);return Math.round(MAXPTS*Math.pow(x,1.5));}
var BANDS=[[0.02,'神準','v0'],[0.07,'很接近','v1'],[0.18,'有概念','v2'],[9,'差很遠','v3']];
function bandOf(e){for(var i=0;i<BANDS.length;i++)if(e<=BANDS[i][0])return BANDS[i];return BANDS[3];}

function totals(){
  var pts=0,done=0,ok=0;
  D.forEach(function(d){var s=state[d.id];if(s&&s.done){done++;pts+=s.pts;if(s.err<=0.18)ok++;}});
  return {pts:pts,done:done,ok:ok};
}
function streakNow(){
  var run=0;var order=state.__order||[];
  for(var i=order.length-1;i>=0;i--){
    var s=state[order[i]];if(s&&s.err<=0.18)run++;else break;
  }
  return run;
}
function updateHUD(){
  var t=totals();
  elScore.innerHTML=t.pts.toLocaleString('en-US')+' <small>分</small>';
  elCnt.textContent=t.done+' / '+D.length;
  elProg.style.width=(100*t.done/D.length).toFixed(1)+'%';
  var st=streakNow();
  if(st>=2){elStreak.hidden=false;elStreak.textContent='🔥 '+st+' 連';}else{elStreak.hidden=true;}
}
function chapterStat(name){
  var items=D.filter(function(d){return d.group===name;});
  var done=items.filter(function(d){return state[d.id]&&state[d.id].done;}).length;
  return {done:done,total:items.length,all:items.length>0&&done===items.length};
}
function renderTabs(){
  var h=CH.map(function(c){
    var st=chapterStat(c[0]);
    return '<button class="tab" type="button" data-tab="'+esc(c[0])+'" aria-current="'+(tab===c[0])+'">'
      +(st.all?'<span class="dot" aria-hidden="true"></span>':'')+esc(c[0])
      +'<span class="tn">'+st.done+'/'+st.total+'</span></button>';
  }).join('');
  h+='<button class="tab sum" type="button" data-tab="summary" aria-current="'+(tab==='summary')+'">總結</button>';
  elTabs.innerHTML=h;
}
function renderPager(){
  if(tab==='summary'){elPager.innerHTML='';return;}
  var i=CH.findIndex(function(c){return c[0]===tab;});
  var prev=i>0?CH[i-1][0]:null, next=i<CH.length-1?CH[i+1][0]:'summary';
  var h=prev?'<button class="btn alt" data-tab="'+esc(prev)+'" type="button">← '+esc(prev)+'</button>':'<span class="sp"></span>';
  h+='<span class="sp"></span>';
  h+='<button class="btn" data-tab="'+esc(next)+'" type="button">'
    +(next==='summary'?'看總結':esc(next)+' →')+'</button>';
  elPager.innerHTML=h;
}

/* ---------- 圖表：一般題（各國分布） ---------- */
function chartRank(d,guess){
  var W=760,H=300,L=56,R=104,T=52,B=36,n=d.n,vals=d.dist;
  var lo=Math.min.apply(null,vals),hi=Math.max.apply(null,vals);
  if(d.oecd!=null){lo=Math.min(lo,d.oecd);hi=Math.max(hi,d.oecd);}
  var pad=(hi-lo)*0.12||1,LO=lo-pad,HI=hi+pad;
  function X(r){return L+(r-1)/(n-1)*(W-L-R);}
  function Y(v){return T+(HI-v)/(HI-LO)*(H-T-B);}
  var pts=vals.map(function(v,k){return X(k+1).toFixed(1)+','+Y(v).toFixed(1);}).join(' ');
  var s='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="'+esc(d.label)
    +'：各國由高到低排列，臺灣第 '+d.rank+' 名，共 '+n+' 個國家或經濟體">';
  s+='<polyline points="'+X(1).toFixed(1)+','+(H-B)+' '+pts+' '+X(n).toFixed(1)+','+(H-B)
    +'" fill="var(--blue-50)"/>';
  s+='<polyline points="'+pts+'" fill="none" stroke="var(--blue-300)" stroke-width="2"/>';
  if(d.oecd!=null){var oy=Y(d.oecd);
    s+='<line x1="'+L+'" y1="'+oy.toFixed(1)+'" x2="'+(W-R)+'" y2="'+oy.toFixed(1)
      +'" stroke="var(--ink-3)" stroke-width="1" stroke-dasharray="4 4"/>';
    s+='<text x="'+(W-R+8)+'" y="'+(oy+4).toFixed(1)+'" font-size="12" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">OECD '+esc(fmt(d.fmt,d.oecd))+'</text>';}
  var placed=[];
  d.marks.slice().sort(function(a,b){return a.r-b.r;}).forEach(function(m){
    var x=X(m.r),y=Y(m.v),w=m.zh.length*12+12,row=0;
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
  if(guess){var gx=X(Math.min(Math.max(guess,1),n));
    s+='<line x1="'+gx.toFixed(1)+'" y1="'+T+'" x2="'+gx.toFixed(1)+'" y2="'+(H-B)
      +'" stroke="var(--ink-3)" stroke-dasharray="2 3"/>';
    s+='<text x="'+gx.toFixed(1)+'" y="'+(H-B+15)+'" font-size="12" text-anchor="middle" fill="var(--ink-3)" font-family="Noto Sans TC,sans-serif">你猜 '+guess+'</text>';}
  var tx=X(d.rank),ty=Y(d.tw);
  s+='<g class="'+(reduce?'':'pop')+'" style="transform-origin:'+tx.toFixed(1)+'px '+ty.toFixed(1)+'px">';
  s+='<line x1="'+tx.toFixed(1)+'" y1="'+(T-20)+'" x2="'+tx.toFixed(1)+'" y2="'+(H-B)+'" stroke="var(--yel-500)" stroke-width="2"/>';
  s+='<circle cx="'+tx.toFixed(1)+'" cy="'+ty.toFixed(1)+'" r="7" fill="var(--yel-500)" stroke="var(--surface)" stroke-width="2"/>';
  var an=d.rank>n*0.7?'end':(d.rank<n*0.16?'start':'middle');
  s+='<text x="'+tx.toFixed(1)+'" y="'+(T-26)+'" font-size="14" font-weight="700" text-anchor="'+an
    +'" fill="var(--yel-700)" font-family="Noto Sans TC,sans-serif">臺灣 第 '+d.rank+' 名</text></g>';
  s+='<line x1="'+L+'" y1="'+(H-B)+'" x2="'+(W-R)+'" y2="'+(H-B)+'" stroke="var(--line)"/>';
  s+='<text x="'+L+'" y="'+(H-B+28)+'" font-size="12" fill="var(--ink-3)" font-family="Noto Sans TC,sans-serif">第 1 名</text>';
  s+='<text x="'+(W-R)+'" y="'+(H-B+28)+'" font-size="12" text-anchor="end" fill="var(--ink-3)" font-family="Noto Sans TC,sans-serif">第 '+n+' 名</text>';
  s+='<text x="'+(L-8)+'" y="'+(T+4)+'" font-size="12" text-anchor="end" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">'+esc(fmt(d.fmt,hi))+'</text>';
  s+='<text x="'+(L-8)+'" y="'+(H-B)+'" font-size="12" text-anchor="end" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">'+esc(fmt(d.fmt,lo))+'</text>';
  return s+'</svg>';
}

/* ---------- 圖表：趨勢題（跨屆折線） ---------- */
function chartTrend(d,guess){
  var W=760,H=330,L=66,R=96,T=56,B=52,cy=d.cycles,n=cy.length;
  var all=[];
  d.tw.forEach(function(v){if(v!=null)all.push(v);});
  if(d.oecd)d.oecd.forEach(function(v){if(v!=null)all.push(v);});
  d.refs.forEach(function(r){r.v.forEach(function(v){if(v!=null)all.push(v);});});
  if(guess!=null)all.push(guess);
  var lo=Math.min.apply(null,all),hi=Math.max.apply(null,all);
  var pad=(hi-lo)*0.14||1,LO=lo-pad,HI=hi+pad;
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
    var rk=d.ranks[i];
    if(rk&&rk[0])s+='<text x="'+X(i).toFixed(1)+'" y="'+(Y(v)-14).toFixed(1)+'" font-size="11" text-anchor="middle" fill="var(--yel-700)" font-family="Noto Sans TC,sans-serif">第 '+rk[0]+'</text>';
  });
  s+='<text x="'+X(0).toFixed(1)+'" y="'+(Y(d.tw[0])+22).toFixed(1)+'" font-size="13" font-weight="700" fill="var(--yel-700)" font-family="Noto Sans TC,sans-serif">臺灣</text>';
  if(guess!=null){
    var gx=X(d.guess_i),gy=Y(guess);
    s+='<circle cx="'+gx.toFixed(1)+'" cy="'+gy.toFixed(1)+'" r="6" fill="none" stroke="var(--ink-3)" stroke-width="2" stroke-dasharray="3 2"/>';
    s+='<text x="'+(gx-10)+'" y="'+(gy+4).toFixed(1)+'" font-size="12" text-anchor="end" fill="var(--ink-3)" font-family="Noto Sans TC,sans-serif">你猜 '+esc(fmt(d.fmt,guess))+'</text>';
  }
  s+='<line x1="'+L+'" y1="'+(H-B)+'" x2="'+(W-R)+'" y2="'+(H-B)+'" stroke="var(--line)"/>';
  s+='<text x="'+(L-8)+'" y="'+(T+4)+'" font-size="12" text-anchor="end" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">'+esc(fmt(d.fmt,HI-pad/2))+'</text>';
  s+='<text x="'+(L-8)+'" y="'+(H-B)+'" font-size="12" text-anchor="end" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">'+esc(fmt(d.fmt,LO+pad/2))+'</text>';
  return s+'</svg>';
}

/* ---------- 卡片 ---------- */
function unitHelp(d){
  if(/\{v:[+]?\.2f\}/.test(d.fmt)&&d.kind!=='points10')
    return '這是一個「指數」：OECD 平均 = 0，正數代表高於國際平均，1.0 大約等於一個標準差。';
  return '';
}
function face(d){
  var s=state[d.id],b;
  if(s&&s.done){b='<span class="badge pts">'+s.pts+' 分 ｜ '+esc(s.band)+'</span>';}
  else b='<span class="badge">未作答</span>';
  return '<h4>'+esc(d.teaser)+'</h4><p class="hook">'+esc(d.hook)+'</p>'
    +'<div class="foot">'+b+'<span class="badge cyc">'+(d.type==='trend'
      ?(d.cycles[0]+'→'+d.cycles[d.cycles.length-1]):('PISA '+d.cycle))+'</span>'+stars(d.surprise)+'</div>';
}
function guessUI(d){
  var s=state[d.id],help=unitHelp(d),given='';
  var lo,hi,step,mid,valLabel;
  if(d.type==='trend'){
    lo=d.rng[0];hi=d.rng[1];step=d.rng[2];
    mid=s?s.guess:d.tw[0];
    given='<div class="given">'+d.cycles.slice(0,d.guess_i).map(function(y,i){
      return d.tw[i]==null?'':'<b>'+y+'：'+esc(fmt(d.fmt,d.tw[i]))+(d.ranks[i][0]?'（第 '+d.ranks[i][0]+' 名）':'')+'</b>';
    }).join('')+'</div>';
    valLabel=esc(fmt(d.fmt,mid));
  }else{
    lo=1;hi=d.n;step=1;mid=s?s.guess:Math.round(d.n/2);
    valLabel='第 '+mid+' 名 <small>／ '+d.n+'</small>';
  }
  return '<div class="detail"><p class="q">'+esc(d.q)+'</p>'
    +'<p class="what">'+esc(d.what)+(help?' '+help:'')+'</p>'+given
    +'<div class="guess"><div class="guess-top"><span>'+(d.type==='trend'?'猜 '+d.cycles[d.guess_i]+' 年的數值':'你的猜測')+'</span>'
    +'<span>'+(d.type==='trend'?esc(d.label):'共 '+d.n+' 個國家／經濟體')+'</span></div>'
    +'<div class="guess-num" id="gn-'+d.id+'">'+valLabel+'</div>'
    +'<input type="range" id="sl-'+d.id+'" min="'+lo+'" max="'+hi+'" step="'+step+'" value="'+mid+'" aria-label="猜測值">'
    +'<div class="ends"><span>'+(d.type==='trend'?esc(fmt(d.fmt,lo)):'第 1 名（世界最高）')+'</span>'
    +'<span>'+(d.type==='trend'?esc(fmt(d.fmt,hi)):'第 '+d.n+' 名（世界最低）')+'</span></div></div>'
    +'<div class="acts"><button class="btn" data-act="reveal" data-id="'+d.id+'" type="button">看答案</button>'
    +'<button class="btn alt" data-act="close" type="button">收起</button></div></div>';
}
function revealUI(d){
  var s=state[d.id],g=s.guess,ans=answerOf(d),band=bandOf(s.err);
  var big,your,tbl;
  if(d.type==='trend'){
    big=esc(fmt(d.fmt,ans))+' <small>'+d.cycles[d.guess_i]+' 年</small>';
    var delta=d.tw[0]==null?null:(ans-d.tw[0]);
    your='你猜 '+fmt(d.fmt,g)+(delta==null?'':'　｜　'+d.cycles[0]+'→'+d.cycles[d.guess_i]+' 變化 '+fmt(d.fmt.replace('{v:.','{v:+.').replace('{v:+:+.','{v:+.'),delta));
    var head='<tr><th>國家／經濟體</th>'+d.cycles.map(function(y){return '<th>'+y+'</th>';}).join('')+'</tr>';
    var body='<tr class="tw"><td>臺灣</td>'+d.tw.map(function(v){return '<td>'+(v==null?'—':esc(fmt(d.fmt,v)))+'</td>';}).join('')+'</tr>';
    body+='<tr class="tw"><td>臺灣的名次</td>'+d.ranks.map(function(r){return '<td>'+(r[0]?'第 '+r[0]+' ／ '+r[1]:'—')+'</td>';}).join('')+'</tr>';
    if(d.oecd)body+='<tr class="oecd"><td>OECD 平均</td>'+d.oecd.map(function(v){return '<td>'+(v==null?'—':esc(fmt(d.fmt,v)))+'</td>';}).join('')+'</tr>';
    d.refs.forEach(function(r){body+='<tr><td>'+esc(r.zh)+'</td>'+r.v.map(function(v){return '<td>'+(v==null?'—':esc(fmt(d.fmt,v)))+'</td>';}).join('')+'</tr>';});
    tbl='<table><caption>'+esc(d.label)+'</caption><thead>'+head+'</thead><tbody>'+body+'</tbody></table>';
  }else{
    big='第 '+ans+' <small>／ '+d.n+'</small>';
    var diff=Math.abs(g-ans);
    your=diff===0?'完全猜中':'你猜第 '+g+' 名，差 '+diff+' 名（'+(g<ans?'比實際樂觀':'比實際保守')+'）';
    var rows='<tr class="tw"><td>臺灣</td><td>'+esc(fmt(d.fmt,d.tw))+'</td><td>第 '+d.rank+'</td></tr>';
    if(d.oecd!=null)rows+='<tr class="oecd"><td>OECD 平均</td><td>'+esc(fmt(d.fmt,d.oecd))+'</td><td>—</td></tr>';
    d.marks.forEach(function(m){rows+='<tr><td>'+esc(m.zh)+'</td><td>'+esc(fmt(d.fmt,m.v))+'</td><td>第 '+m.r+'</td></tr>';});
    rows+='<tr class="oecd"><td>世界最高 ｜ '+esc(d.best.zh)+'</td><td>'+esc(fmt(d.fmt,d.best.v))+'</td><td>第 1</td></tr>';
    rows+='<tr class="oecd"><td>世界最低 ｜ '+esc(d.worst.zh)+'</td><td>'+esc(fmt(d.fmt,d.worst.v))+'</td><td>第 '+d.n+'</td></tr>';
    tbl='<table><caption>'+esc(d.label)+'（PISA '+d.cycle+'）</caption>'
      +'<thead><tr><th>國家／經濟體</th><th>數值</th><th>排名</th></tr></thead><tbody>'+rows+'</tbody></table>';
  }
  return '<div class="detail"><p class="q">'+esc(d.q)+'</p>'
    +'<p class="what">'+esc(d.what)+'</p>'
    +'<div class="judge"><span class="big" id="big-'+d.id+'">'+big+'</span>'
    +'<span class="verdict '+band[2]+'">'+band[1]+'</span>'
    +'<span class="gain">+'+s.pts+' 分</span><span class="your">'+esc(your)+'</span></div>'
    +'<div class="chartwrap">'+(d.type==='trend'?chartTrend(d,g):chartRank(d,g))+'</div>'
    +tbl+'<p class="insight">'+esc(d.note)+'</p>'
    +'<p class="src">資料表：'+esc(d.src)+'</p>'
    +'<div class="acts"><button class="btn alt" data-act="close" type="button">收起</button>'
    +'<button class="btn alt" data-act="retry" data-id="'+d.id+'" type="button">重猜這題</button></div></div>';
}

function render(){
  renderTabs();renderPager();
  if(tab==='summary'){board.innerHTML='';renderSummary();updateHUD();return;}
  var c=CH.filter(function(x){return x[0]===tab;})[0]||CH[0];
  var items=D.filter(function(d){return d.group===c[0];});
  var st=chapterStat(c[0]);
  var html='<section class="chapter"><div class="chapter-h"><i></i><h3>'+esc(c[0])+'</h3><em>'
    +esc(c[1])+'</em><span class="cs">'+st.done+' / '+st.total+' 已揭曉</span></div><div class="grid">';
  items.forEach(function(d){
    var open=openId===d.id,tag=open?'div':'button';
    html+='<'+tag+' class="qcard'+(open?' open':'')+'" '+(open?'':'type="button" ')
      +'data-card="'+d.id+'">'+face(d)
      +(open?(state[d.id]&&state[d.id].done?revealUI(d):guessUI(d)):'')+'</'+tag+'>';
  });
  html+='</div></section>';
  board.innerHTML=html;
  updateHUD();
  var sl=openId&&document.getElementById('sl-'+openId);
  if(sl){
    var d=byId(openId),gn=document.getElementById('gn-'+openId);
    sl.addEventListener('input',function(){
      gn.innerHTML=d.type==='trend'?esc(fmt(d.fmt,+sl.value))
        :('第 '+sl.value+' 名 <small>／ '+d.n+'</small>');
    });
  }
  if(justRevealed){rollNumber(justRevealed);justRevealed=null;}
}

function rollNumber(id){
  if(reduce)return;
  var d=byId(id),el=document.getElementById('big-'+id);
  if(!el)return;
  var s=state[id],from=s.guess,to=answerOf(d),t0=null,dur=650;
  var tail=el.querySelector('small').outerHTML;
  function frame(ts){
    if(!t0)t0=ts;
    var p=Math.min(1,(ts-t0)/dur),e=1-Math.pow(1-p,3),v=from+(to-from)*e;
    el.innerHTML=(d.type==='trend'?esc(fmt(d.fmt,v)):('第 '+Math.round(v)+' '))+' '+tail;
    if(p<1)requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
}

function goTab(name){
  if(tab===name)return;
  tab=name;openId=null;saveTab();render();
  var top=elTabs.getBoundingClientRect().top+window.scrollY-8;
  window.scrollTo({top:Math.max(0,top),behavior:reduce?'auto':'smooth'});
}
elTabs.addEventListener('click',function(ev){
  var b=ev.target.closest('[data-tab]');if(b)goTab(b.getAttribute('data-tab'));});
elPager.addEventListener('click',function(ev){
  var b=ev.target.closest('[data-tab]');if(b)goTab(b.getAttribute('data-tab'));});

board.addEventListener('click',function(ev){
  var act=ev.target.closest('[data-act]');
  if(act){
    var a=act.getAttribute('data-act');
    if(a==='close'){openId=null;render();return;}
    if(a==='reveal'){
      var id=act.getAttribute('data-id'),d=byId(id),sl=document.getElementById('sl-'+id);
      var g=+sl.value,e=errOf(d,g),b=bandOf(e);
      state[id]={guess:g,done:true,err:e,pts:pointsOf(e),band:b[1]};
      state.__order=(state.__order||[]).filter(function(x){return x!==id;}).concat([id]);
      save();justRevealed=id;render();
      var el=document.querySelector('[data-card="'+id+'"]');
      if(el)el.scrollIntoView({behavior:reduce?'auto':'smooth',block:'center'});
      return;
    }
    if(a==='retry'){var id2=act.getAttribute('data-id');delete state[id2];
      state.__order=(state.__order||[]).filter(function(x){return x!==id2;});
      save();render();return;}
  }
  var card=ev.target.closest('[data-card]');
  if(card&&card.tagName==='BUTTON'){
    openId=card.getAttribute('data-card');render();
    var el2=document.querySelector('[data-card="'+openId+'"]');
    if(el2)el2.scrollIntoView({behavior:reduce?'auto':'smooth',block:'center'});
  }
});

var TITLES=[[0.30,'直覺派','你多半是照「臺灣考試很強」的印象在推論——這正是這份資料最想戳破的地方。'],
            [0.50,'略懂觀察者','你抓到了一部分，但態度面與結構面還是比你想的更極端。'],
            [0.70,'資料讀者','你知道成績和其他面向會脫鉤，方向大致抓得住。'],
            [0.85,'教育現場派','你對臺灣教育的落差與矛盾有相當準確的體感。'],
            [1.01,'PISA 解讀者','你幾乎預測到了每一個反直覺的位置。']];
function renderSummary(){
  var t=totals(),max=D.length*MAXPTS,ratio=t.done?t.pts/(t.done*MAXPTS):0;
  var title=TITLES[0];for(var i=0;i<TITLES.length;i++){if(ratio<TITLES[i][0]){title=TITLES[i];break;}}
  var head;
  if(t.done===0){
    head='<p class="insight">還沒有揭曉任何一題。先挑一張卡片猜猜看，這裡會統計你的分數與準確度。</p>';
  }else{
    var signed=0;D.forEach(function(d){var s=state[d.id];if(!s||!s.done)return;
      var ans=answerOf(d);signed+=(d.type==='trend'?0:(ans-s.guess));});
    var rankDone=D.filter(function(d){return d.type!=='trend'&&state[d.id]&&state[d.id].done;}).length;
    head='<div class="title-card"><div class="lv">YOUR LEVEL</div><h3>'+esc(title[1])+'</h3>'
      +'<p>'+esc(title[2])+'</p></div>'
      +'<div class="stats"><div><b>'+t.pts.toLocaleString('en-US')+'</b><span>總分（滿分 '+max.toLocaleString('en-US')+'）</span></div>'
      +'<div><b>'+t.done+'</b><span>已揭曉題數</span></div>'
      +'<div><b>'+t.ok+'</b><span>猜到「有概念」以上</span></div>'
      +'<div><b>'+Math.round(100*ratio)+'%</b><span>平均準確度</span></div></div>';
    if(rankDone>=3){
      var avg=signed/rankDone;
      head+='<p class="insight">'+(avg>0?'在排名題上，你平均把臺灣猜得比實際<b>好 '+Math.abs(avg).toFixed(1)+' 名</b>。'
        :(avg<0?'在排名題上，你平均把臺灣猜得比實際<b>差 '+Math.abs(avg).toFixed(1)+' 名</b>。':'你沒有系統性偏誤。'))
        +'多數人會高估臺灣在態度、動機、自信上的位置——因為我們太習慣用成績排名去推論其他一切。</p>';
    }
  }
  board.innerHTML='<div class="panel"><h2>臺灣科學教育的體質</h2>'+head
    +'<div class="two">'
    +'<div class="box up"><h4>✓ 真正的強項</h4><ul>'
    +'<li>科學成績世界 <b>第 4</b>，2006／2015／2025 三屆不動</li>'
    +'<li>頂尖學生從 2012 年的 8.3% 衝到 <b>20.1%</b>，世界第 3</li>'
    +'<li>女生科學 <b>545 分</b> 世界第 3，2025 年首度反超男生 10.5 分</li>'
    +'<li>「解釋現象」是三種科學能力中的相對強項，世界 <b>第 5</b></li>'
    +'<li>課堂秩序世界 <b>第 9</b>；蹺課率 <b>10.6%</b>（OECD 33.9%）</li>'
    +'<li>教師支持十年進步 <b>0.26</b>，是改善幅度最大的項目</li>'
    +'</ul></div>'
    +'<div class="box down"><h4>⚠ 二十年沒解決的弱項</h4><ul>'
    +'<li>成長心態 <b>第 82 ／ 90</b>，只有 45.5% 相信智力能改變（日本 76%、韓國 78%）</li>'
    +'<li>應變信心 <b>第 81 ／ 83</b>；好奇心 <b>第 66 ／ 87</b></li>'
    +'<li>「判斷資訊做決策」是相對最弱的能力 <b>第 82 ／ 85</b>；2006 年「辨識科學議題」也是倒數第二</li>'
    +'<li>城鄉分數差 <b>102 分</b>（OECD 32 分）；鄉村學校 454 分，低於 OECD 平均</li>'
    +'<li>補習的社經落差 <b>22 個百分點</b>（OECD 3.4），世界倒數第二</li>'
    +'<li>高低分差距從 2012 年的 215 分擴大到 <b>281 分</b>，十三年持續拉開</li>'
    +'</ul></div></div>'
    +'<p class="insight"><b>一句話：臺灣學生很會解釋老師教過的科學，不太會對沒教過的事情提問、判斷與行動；'
    +'而且愈往鄉村，連「會解釋」都做不到。</b>成績掩蓋了這兩件事整整二十年。</p>'
    +'<div class="acts"><button class="btn" id="back" type="button">回到題目</button>'
    +'<button class="btn alt" id="clr" type="button">清除我的作答紀錄</button></div></div>';
  document.getElementById('clr').addEventListener('click',function(){
    state={};save();openId=null;tab=CH[0][0];saveTab();render();
    window.scrollTo({top:0,behavior:reduce?'auto':'smooth'});});
  document.getElementById('back').addEventListener('click',function(){goTab(CH[0][0]);});
}

render();
})();
