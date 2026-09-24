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

try{var raw=localStorage.getItem('pisa-tw-v3');if(raw)state=JSON.parse(raw)||{};}catch(e){state={};}
try{var tb=localStorage.getItem('pisa-tw-tab');
  if(tb&&(tb==='summary'||CH.some(function(c){return c[0]===tb;})))tab=tb;}catch(e){}
function saveTab(){try{localStorage.setItem('pisa-tw-tab',tab);}catch(e){}}
function save(){try{localStorage.setItem('pisa-tw-v3',JSON.stringify(state));}catch(e){}}

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
function answerOf(d){return d.type==='trend'?d.tw[d.guess_i]:d.pos;}
function errOf(d,g){
  if(d.type==='trend'){var sp=d.rng[1]-d.rng[0];return Math.abs(g-answerOf(d))/sp;}
  return Math.abs(g-d.pos)/100;
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

/* ---------- 圖表：一般題（各國由低到高排成光譜） ---------- */
function chartRank(d,guess){
  var W=760,H=300,L=56,R=104,T=52,B=40,n=d.n,vals=d.dist;
  var lo=Math.min.apply(null,vals),hi=Math.max.apply(null,vals);
  if(d.oecd!=null){lo=Math.min(lo,d.oecd);hi=Math.max(hi,d.oecd);}
  var pad=(hi-lo)*0.12||1,LO=lo-pad,HI=hi+pad;
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
    s+='<text x="'+(W-R+8)+'" y="'+(oy+4).toFixed(1)+'" font-size="12" fill="var(--ink-3)" font-family="Fira Sans,sans-serif">OECD '+esc(fmt(d.fmt,d.oecd))+'</text>';}
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
  if(guess!=null){var gx=X(Math.min(Math.max(guess,0),100));
    s+='<line x1="'+gx.toFixed(1)+'" y1="'+T+'" x2="'+gx.toFixed(1)+'" y2="'+(H-B)
      +'" stroke="var(--ink-3)" stroke-dasharray="2 3"/>';
    s+='<text x="'+gx.toFixed(1)+'" y="'+(H-B+15)+'" font-size="12" text-anchor="middle" fill="var(--ink-3)" font-family="Noto Sans TC,sans-serif">你猜的位置</text>';}
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
function goodPole(d){return lowBetter(d)?d.poles[0]:d.poles[1];}
function scaleHint(d){
  var h='本題納入 '+d.n+' 個國家／經濟體，由左到右排成一條光譜：最左邊是最「'+d.poles[0]
    +'」的國家，最右邊是最「'+d.poles[1]+'」的國家。把滑桿拉到你覺得臺灣所在的位置。';
  return h+(d.neutral?'這題沒有絕對的好壞，看的是偏向哪一邊。':'對學生來說，愈靠「'+goodPole(d)+'」那一邊愈好。');
}
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
      return d.tw[i]==null?'':'<b>'+y+'：'+esc(fmt(d.fmt,d.tw[i]))+'</b>';
    }).join('')+'</div>';
    valLabel=esc(fmt(d.fmt,mid));
  }else{
    lo=0;hi=100;step=1;mid=s?s.guess:50;
    valLabel=esc(zone(d,mid));
  }
  return '<div class="detail"><p class="q">'+esc(d.q)+'</p>'
    +'<p class="what">'+esc(d.what)+(help?' '+help:'')+'</p>'
    +'<p class="scalehint">'+esc(d.type==='trend'
        ?(d.neutral?'這題沒有絕對的好壞，看的是走勢的方向與幅度。'
          :(lowBetter(d)?'這個數字愈小愈好。':'這個數字愈大愈好。'))
        :scaleHint(d))+'</p>'+given
    +'<div class="guess"><div class="guess-top"><span>'+(d.type==='trend'?'猜 '+d.cycles[d.guess_i]+' 年的數值':'你的猜測')+'</span>'
    +'<span>'+(d.type==='trend'?esc(d.label):d.n+' 個國家／經濟體的光譜')+'</span></div>'
    +'<div class="guess-num" id="gn-'+d.id+'">'+valLabel+'</div>'
    +'<input type="range" id="sl-'+d.id+'" min="'+lo+'" max="'+hi+'" step="'+step+'" value="'+mid+'" aria-label="猜測值"'+(d.type==='trend'?'':' aria-valuetext="'+esc(zone(d,mid))+'"')+'>'
    +'<div class="ends"><span>'+(d.type==='trend'?esc(fmt(d.fmt,lo)):esc(endLabels(d)[0]))+'</span>'
    +'<span>'+(d.type==='trend'?esc(fmt(d.fmt,hi)):esc(endLabels(d)[1]))+'</span></div></div>'
    +'<div class="acts"><button class="btn" data-act="reveal" data-id="'+d.id+'" type="button">看答案</button>'
    +'<button class="btn alt" data-act="close" type="button">收起</button></div></div>';
}
function revealUI(d){
  var s=state[d.id],g=s.guess,ans=answerOf(d),band=bandOf(s.err);
  var vw=d.type==='trend'?null:verdictWord(d);
  var place=d.type==='trend'?trendPlacement(d):placement(d);
  var big,your,tbl;
  if(d.type==='trend'){
    big=esc(fmt(d.fmt,ans))+' <small>'+d.cycles[d.guess_i]+' 年</small>';
    var delta=d.tw[0]==null?null:(ans-d.tw[0]);
    your='你猜 '+fmt(d.fmt,g)+(delta==null?'':'　｜　'+d.cycles[0]+'→'+d.cycles[d.guess_i]+' 變化 '+fmt(d.fmt.replace('{v:.','{v:+.').replace('{v:+:+.','{v:+.'),delta));
    var head='<tr><th>國家／經濟體</th>'+d.cycles.map(function(y){return '<th>'+y+'</th>';}).join('')+'</tr>';
    var body='<tr class="tw"><td>臺灣</td>'+d.tw.map(function(v){return '<td>'+(v==null?'—':esc(fmt(d.fmt,v)))+'</td>';}).join('')+'</tr>';
    body+='<tr class="tw"><td>臺灣在各國中的位置</td>'+d.pos.map(function(p){return '<td>'+esc(zone(d,p))+'</td>';}).join('')+'</tr>';
    if(d.oecd)body+='<tr class="oecd"><td>OECD 平均</td>'+d.oecd.map(function(v){return '<td>'+(v==null?'—':esc(fmt(d.fmt,v)))+'</td>';}).join('')+'</tr>';
    d.refs.forEach(function(r){body+='<tr><td>'+esc(r.zh)+'</td>'+r.v.map(function(v){return '<td>'+(v==null?'—':esc(fmt(d.fmt,v)))+'</td>';}).join('')+'</tr>';});
    tbl='<table><caption>'+esc(d.label)+'</caption><thead>'+head+'</thead><tbody>'+body+'</tbody></table>';
  }else{
    big=esc(zone(d,ans));
    var diff=g-ans;
    your=Math.abs(diff)<=3?'你猜的位置幾乎完全正確'
      :'你猜「'+zone(d,g)+'」，比實際更偏向「'+(diff>0?d.poles[1]:d.poles[0])+'」';
    var rows='<tr class="tw"><td>臺灣</td><td>'+esc(fmt(d.fmt,d.tw))+'</td><td>'+esc(zone(d,d.pos))+'</td></tr>';
    if(d.oecd!=null)rows+='<tr class="oecd"><td>OECD 平均</td><td>'+esc(fmt(d.fmt,d.oecd))+'</td><td>—</td></tr>';
    d.marks.forEach(function(m){rows+='<tr><td>'+esc(m.zh)+'</td><td>'+esc(fmt(d.fmt,m.v))+'</td><td>'+esc(zone(d,m.p))+'</td></tr>';});
    rows+='<tr class="oecd"><td>最右端（'+esc(d.poles[1])+'）｜ '+esc(d.top.zh)+'</td><td>'+esc(fmt(d.fmt,d.top.v))+'</td><td>—</td></tr>';
    rows+='<tr class="oecd"><td>最左端（'+esc(d.poles[0])+'）｜ '+esc(d.bottom.zh)+'</td><td>'+esc(fmt(d.fmt,d.bottom.v))+'</td><td>—</td></tr>';
    tbl='<table><caption>'+esc(d.label)+'（PISA '+d.cycle+'）</caption>'
      +'<thead><tr><th>國家／經濟體</th><th>數值</th><th>在光譜上的位置</th></tr></thead><tbody>'+rows+'</tbody></table>';
  }
  return '<div class="detail"><p class="q">'+esc(d.q)+'</p>'
    +'<p class="what">'+esc(d.what)+'</p>'
    +'<div class="judge"><span class="big" id="big-'+d.id+'">'+big+'</span>'
    +(vw?'<span class="verdict '+vw[1]+'">'+esc(vw[0])+'</span>':'')
    +'<span class="verdict vg">'+band[1]+' +'+s.pts+' 分</span>'
    +'<span class="your">'+esc(your)+'</span></div>'
    +'<p class="place">'+esc(place)+'</p>'
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
      gn.innerHTML=d.type==='trend'?esc(fmt(d.fmt,+sl.value)):esc(zone(d,+sl.value));
      if(d.type!=='trend')sl.setAttribute('aria-valuetext',zone(d,+sl.value));
    });
  }
  if(justRevealed){rollNumber(justRevealed);justRevealed=null;}
}

function rollNumber(id){
  if(reduce)return;
  var d=byId(id),el=document.getElementById('big-'+id);
  if(!el||d.type!=='trend')return;
  var s=state[id],from=s.guess,to=answerOf(d),t0=null,dur=650;
  var tail=el.querySelector('small').outerHTML;
  function frame(ts){
    if(!t0)t0=ts;
    var p=Math.min(1,(ts-t0)/dur),e=1-Math.pow(1-p,3),v=from+(to-from)*e;
    el.innerHTML=esc(fmt(d.fmt,v))+' '+tail;
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
    var signed=0,rankDone=0;D.forEach(function(d){var s=state[d.id];
      if(!s||!s.done||d.type==='trend'||d.neutral)return;
      rankDone++;signed+=(lowBetter(d)?-1:1)*(s.guess-d.pos);});
    head='<div class="title-card"><div class="lv">YOUR LEVEL</div><h3>'+esc(title[1])+'</h3>'
      +'<p>'+esc(title[2])+'</p></div>'
      +'<div class="stats"><div><b>'+t.pts.toLocaleString('en-US')+'</b><span>總分（滿分 '+max.toLocaleString('en-US')+'）</span></div>'
      +'<div><b>'+t.done+'</b><span>已揭曉題數</span></div>'
      +'<div><b>'+t.ok+'</b><span>猜到「有概念」以上</span></div>'
      +'<div><b>'+Math.round(100*ratio)+'%</b><span>平均準確度</span></div></div>';
    if(rankDone>=3){
      var avg=signed/rankDone;
      head+='<p class="insight">'+(avg>5?'整體來說，你把臺灣放在比實際<b>更好的位置</b>。'
        :(avg<-5?'整體來說，你把臺灣放在比實際<b>更差的位置</b>。':'整體來說，你的猜測沒有明顯偏好或偏壞。'))
        +'多數人會高估臺灣在態度、動機、自信上的位置——因為我們太習慣用成績去推論其他一切。</p>';
    }
  }
  board.innerHTML='<div class="panel"><h2>臺灣科學教育的體質</h2>'+head
    +'<div class="two">'
    +'<div class="box up"><h4>✓ 表現較佳的面向</h4><ul>'
    +'<li>科學成績三個主測年都在<b>分數最高的那一端</b></li>'
    +'<li>頂尖學生 <b>20.1%</b>，落在頂尖學生最多的那一端；2012 年以來成長約 2.4 倍，但中間 2018 年曾回落</li>'
    +'<li>女生科學 <b>545 分</b>，落在分數最高的那一端；2025 年首度反超男生 10.5 分</li>'
    +'<li>三項科學能力中，「解釋現象」是臺灣的<b>相對強項</b></li>'
    +'<li>課堂落在<b>有秩序的那一端</b>；蹺課率 <b>10.6%</b>（OECD 33.9%）</li>'
    +'<li>教師支持十年進步 <b>0.26</b>，在各國之中往「支持多」的方向移動</li>'
    +'</ul></div>'
    +'<div class="box down"><h4>⚠ 表現落後的面向</h4><ul>'
    +'<li>成長心態落在<b>最不相信能變聰明的那一端</b>：45.5% 不同意「智力無法改變」（OECD 69.3%、日本 76.0%、韓國 77.9%；香港 44.1%、中國四省市 49.6% 同樣偏低）</li>'
    +'<li>應變信心落在<b>最沒信心的那一端</b>；好奇心複合指數<b>偏沒好奇心</b>（但「我對很多事情都感到好奇」單題 73.2%，與 OECD 73.5% 相當）</li>'
    +'<li>三項科學能力中，「評估資訊做決策」是臺灣的<b>相對弱項</b>；其絕對分數 528 分仍高於 OECD 的 480 分</li>'
    +'<li>城鄉分數差 <b>102 分</b>（OECD 32 分）；鄉村學校 454 分，低於 OECD 平均 458 分</li>'
    +'<li>補習的社經落差 <b>22 個百分點</b>（OECD 3.4），落在<b>落差最大的那一端</b></li>'
    +'<li>高低分差距 2012 年 215 分、2025 年 <b>281 分</b>，整體擴大但非逐屆遞增</li>'
    +'</ul></div></div>'
    +'<p class="insight"><b>怎麼讀這份資料：</b>臺灣學生的科學成績穩定位居前段，高分群也持續擴大。'
    +'同一份資料同時顯示三件事：學習信念（成長心態、應變信心）明顯低於 OECD；三項科學能力當中，'
    +'「評估資訊做決策」是相對最不突出的一項（但絕對分數仍高於 OECD）；城鄉與社經落差偏大。'
    +'這些是不同面向的指標，彼此可能相關，但不能互相推論——成績好不代表信念強，'
    +'相對弱項也不等於學生「不會」。</p>'
    +'<div class="acts"><button class="btn" id="back" type="button">回到題目</button>'
    +'<button class="btn alt" id="clr" type="button">清除我的作答紀錄</button></div></div>';
  document.getElementById('clr').addEventListener('click',function(){
    state={};save();openId=null;tab=CH[0][0];saveTab();render();
    window.scrollTo({top:0,behavior:reduce?'auto':'smooth'});});
  document.getElementById('back').addEventListener('click',function(){goTab(CH[0][0]);});
}

render();
})();
