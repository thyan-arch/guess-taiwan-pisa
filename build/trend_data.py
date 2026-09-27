# -*- coding: utf-8 -*-
"""趨勢題資料：從 OECD 官方跨屆對照表抽出完整時間序列"""
import json, os, sys, openpyxl
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from qtext import TREND, MORE_WORD, NEUTRAL, POLES
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
RAW=os.path.join(ROOT,'raw')
_c={}
def rows(f,s):
    k=(f,s)
    if k not in _c:
        wb=openpyxl.load_workbook(os.path.join(RAW,f),read_only=True,data_only=True)
        _c[k]=[list(r) for r in wb[s].iter_rows(values_only=True)]
    return _c[k]
def num(v):
    if isinstance(v,(int,float)): return float(v)
    return None
ALIAS={'Czech Republic':'Czechia','Turkey':'Türkiye','B-S-J-G (China)':'B-S-J-Z (China)'}
def canon(n):
    n=str(n).strip()
    n=ALIAS.get(n,n)
    return ALIAS.get(n.rstrip('*').strip(),n.rstrip('*').strip())
ZH={'Chinese Taipei':'臺灣','Japan':'日本','Korea':'韓國','United States':'美國',
    'Singapore':'新加坡','Finland':'芬蘭','B-S-J-Z (China)':'中國四省市'}
REF=['Japan','Korea','United States','Singapore','Finland']

def series(f,sheet,cols,flip=False):
    """回傳 {country:[v per cycle]} 與 oecd list"""
    rs=rows(f,sheet)
    st=[i for i,r in enumerate(rs) if r and r[0] and str(r[0]).strip()=='OECD average'][0]
    out={};oecd=None
    for r in rs[st:]:
        if not r or r[0] is None: continue
        nm=str(r[0]).strip()
        if not nm or len(nm)>45 or ':' in nm: 
            if nm.lower().startswith(('note','source','informa','symbol','countries and','for all')): break
            continue
        vals=[]
        for c in cols:
            v=num(r[c]) if c<len(r) else None
            vals.append(None if v is None else (-v if flip else round(v,3)))
        if nm=='OECD average': oecd=vals; continue
        if all(v is None for v in vals): continue
        out[canon(nm)]=vals
    return out,oecd

def pos_of(data,country,i):
    """光譜位置 0–100：比臺灣數值低的國家占多少"""
    vs=[v[i] for c,v in data.items() if v[i] is not None]
    t=data[country][i]
    if t is None: return None
    return round(100*sum(1 for x in vs if x<t)/max(1,len(vs)-1),1)

def rank_of(data,country,i,hib):
    vs=[(v[i],c) for c,v in data.items() if v[i] is not None]
    vs.sort(reverse=hib)
    for k,(v,c) in enumerate(vs):
        if c==country: return k+1,len(vs)
    return None,len(vs)

F2,F3,F4,F6,F7='b1_2_2025.xlsx','b1_3_2025.xlsx','b1_4_2025.xlsx','b1_6_2025.xlsx','b1_7_2025.xlsx'
SEVEN=[2006,2009,2012,2015,2018,2022,2025]

SPEC=[
 dict(id='t_sci_mean',teaser='成績的十九年',hook='七屆走下來，是進步還是退步',
   f=F2,sheet='Table I.B1.2a.36',cols=[1,3,5,7,9,11,13],cycles=SEVEN,hib=True,
   fmt='{v:.0f} 分',label='科學平均分數',rng=[470,580,1],
   q='2006 年臺灣科學 532 分（在各國中落在分數最高的那一端）。十九年、七屆之後，2025 年是幾分？',
   note='十九年、七次評量，臺灣的科學平均分數一直在各國的前段，但不是一直往上：2009 年（520 分）和 2018 年（516 分）各掉過一次，2025 年來到 540 分，比 2006 年的 532 分稍高。白話說，臺灣的科學成績很穩，有起伏，但沒有長期退步。'),
 dict(id='t_spread',teaser='差距的十九年',hook='前段與後段的距離，變近還是變遠',
   f=F2,sheet='Table I.B1.2a.42',cols=[3,7,11,15,19,23,27],cycles=SEVEN,hib=False,
   fmt='{v:.0f} 分',label='科學高低分差距（P90−P10）',rng=[190,320,1],
   q='2006 年臺灣前段與後段學生的科學分數差是 249 分。2025 年呢？',
   note='前 10% 和後 10% 學生的分數差，2012 年是 215 分（歷屆最小），2025 年拉大到 281 分。拆開看：2012 到 2025 年，前 10% 的門檻分數高了約 46 分，後 10% 的門檻低了約 20 分——兩端都在拉開，但主要是高分那一端拉得更遠。2018 年曾小幅收斂，所以不是每一屆都在擴大。'),
 dict(id='t_top',teaser='頂尖學生的十九年',hook='世界級的臺灣學生變多還是變少',
   f=F2,sheet='Table I.B1.2a.33',cols=[3,7,11,15,19,23,27],cycles=SEVEN,hib=True,
   fmt='{v:.1f}%',label='科學頂尖學生（L5–6）比例',rng=[3,25,0.1],
   q='2006 年臺灣有 14.6% 的學生達到科學最高等級。2025 年這個比例是多少？',
   note='達到科學最高兩級的臺灣學生，從 2012 年的 8.3% 增加到 2025 年的 20.1%，大約是 2.4 倍。但不是每一屆都在增加：2018 年曾從 15.4% 掉回 11.7%。白話說，整體來看，臺灣的頂尖學生明顯變多了。'),
 dict(id='t_low',teaser='後段學生的十九年',hook='跟頂尖同時發生的另一件事',
   f=F2,sheet='Table I.B1.2a.33',cols=[1,5,9,13,17,21,25],cycles=SEVEN,hib=False,
   fmt='{v:.1f}%',label='科學未達基礎水準（L2 以下）比例',rng=[5,20,0.1],
   q='2012 年臺灣只有 9.8% 的學生沒達到科學基礎水準，是歷屆最低。2025 年呢？',
   note='沒達到科學基本門檻的學生，2012 年是 9.8%（歷屆最低），2025 年是 12.9%，中間 2018 年一度到 15.1%。白話說，頂尖學生變多的同時，跟不上的學生也比 2012 年多了。不過跟 OECD 平均（25.7%）比，臺灣後段學生的比例仍然低很多。'),
 dict(id='t_gender',teaser='性別的十年',hook='男生領先，還是女生領先',
   f=F4,sheet='Table I.B1.2c.25',cols=[1,7,13,19],cycles=[2015,2018,2022,2025],hib=None,flip=True,
   fmt='{v:+.1f} 分',label='科學成績性別差（女生減男生）',rng=[-25,25,0.5],
   q='2015 年臺灣男生的科學成績領先女生 4.5 分。2025 年的差距是多少？（正值代表女生領先）',
   note='2015 到 2022 年都是男生小幅領先，2025 年變成女生領先 10.5 分。這不是臺灣獨有的變化：同一段期間，OECD 平均也從男生領先變成女生小幅領先（1.2 分），克羅埃西亞、以色列等十多個國家／經濟體也一樣翻轉。臺灣比較特別的是，女生不只領先男生，成績也在各國女生裡最前面的那一群。'),
 dict(id='t_enjoy',teaser='樂趣的十年',hook='這題臺灣其實在變好',
   f=F6,sheet='Table I.B1.3.54',cols=[1,4],cycles=[2015,2025],hib=True,
   fmt='{v:+.2f}',label='享受科學（樂趣）指數',rng=[-0.6,0.6,0.01],
   q='2015 年臺灣學生「享受科學」的指數是 −0.06（低於 OECD 平均）。2025 年呢？',
   note='跟 2015 年比，臺灣學生比較喜歡學科學了：指數從 −0.06 升到 +0.05，從低於 OECD 平均變成略高於平均。不過放到各國之中，只是從「最不覺得有趣的那一群」移到「中間偏不覺得有趣」。白話說，有進步，但還稱不上喜歡。'),
 dict(id='t_teacher',teaser='教師支持的十年',hook='學生感受到的老師支持，變多還是變少',
   f=F7,sheet='Table I.B1.4.115',cols=[1,4],cycles=[2015,2025],hib=True,
   fmt='{v:+.2f}',label='科學課的教師支持指數',rng=[-0.4,0.7,0.01],
   q='2015 年臺灣「科學課教師支持」指數是 +0.06，只比 OECD 平均高一點。2025 年呢？',
   note='學生感受到的老師支持，十年來明顯增加：指數從 +0.06 升到 +0.33，進步 0.26，也比 OECD 平均（+0.04）高出不少。白話說，比起 2015 年，現在有更多臺灣學生覺得科學老師會關心他們的學習、會多幫忙、會確認大家都聽懂。'),
 dict(id='t_escs',teaser='社經影響力的十年',hook='家庭背景的力量變大還是變小',
   f=F3,sheet='Table I.B1.2b.25',cols=[1,3,5,7],cycles=[2015,2018,2022,2025],hib=False,
   fmt='{v:.1f}%',label='社經地位可解釋的科學成績變異％',rng=[4,24,0.1],
   q='2015 年臺灣有 14.1% 的科學成績差異可以用家庭社經地位解釋。2025 年呢？',
   note='家庭社經背景能解釋的科學成績差異，從 2015 年的 14.1% 降到 2025 年的 11.4%，略低於 OECD 平均（11.6%）；但中間有起伏，2022 年曾回升到 13.3%。白話說，單看這個指標，家庭背景對臺灣學生成績的影響，沒有比其他國家大。不過城鄉分數差 102 分、補習機會的家庭差距 22 個百分點，都顯示其他面向的落差仍然明顯。'),
]

out=[]
for sp in SPEC:
    data,oecd=series(sp['f'],sp['sheet'],sp['cols'],sp.get('flip',False))
    tw=data.get('Chinese Taipei')
    if not tw: print('!! 缺臺灣',sp['id']); continue
    gi=len(sp['cycles'])-1
    hib=sp['hib'] if sp['hib'] is not None else True
    ranks=[]
    for k in range(len(sp['cycles'])):
        r,n=rank_of(data,'Chinese Taipei',k,hib)
        ranks.append([r,n])
    out.append({
      'type':'trend','group':'趨勢','id':sp['id'],'teaser':sp['teaser'],'hook':sp['hook'],
      'q':sp['q'],'note':sp['note'],'what':TREND[sp['id']],'fmt':sp['fmt'],'label':sp['label'],
      'cycles':sp['cycles'],'guess_i':gi,'rng':sp['rng'],
      'tw':tw,'oecd':oecd,'ranks':ranks,'pos':[pos_of(data,'Chinese Taipei',k) for k in range(len(sp['cycles']))],
      'poles':POLES[sp['id']],
      'refs':[{'zh':ZH[c],'v':data[c]} for c in REF if c in data],
      'surprise':round(abs(100*(ranks[gi][0]-1)/max(1,ranks[gi][1]-1)
                           -100*(ranks[0][0]-1)/max(1,ranks[0][1]-1)),1),
      'src':f"{sp['f']} / {sp['sheet']}",
      'hib':sp['hib'],'kind':('pct' if '%' in sp['fmt'] else ('score' if '分' in sp['fmt'] else 'index')),
      'moreWord':MORE_WORD.get(sp['id'],'高'),'neutral':sp['id'] in NEUTRAL,
    })
    print(f"  {sp['id']:<12} 臺灣 {tw}  排名 {[r[0] for r in ranks]}")
json.dump(out,open(os.path.join(ROOT,'data','trend_data.json'),'w',encoding='utf-8'),
          ensure_ascii=False,separators=(',',':'))
print(len(out),'題趨勢；',os.path.getsize(os.path.join(ROOT,'data','trend_data.json')),'bytes')
