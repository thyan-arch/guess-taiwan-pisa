# -*- coding: utf-8 -*-
"""趨勢題資料：從 OECD 官方跨屆對照表抽出完整時間序列"""
import json, os, sys, openpyxl
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from qtext import TREND, MORE_WORD, NEUTRAL
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
   q='2006 年臺灣科學 532 分（世界第 4）。十九年、七屆之後，2025 年是幾分？',
   note='539.7 分，世界第 4。七屆的名次幾乎沒動過（4、11、10、4、10、4、4），但中間掉過兩次：2009 年 520 分、2018 年 516 分。總體是回到原點再往上一點。'),
 dict(id='t_spread',teaser='差距的十九年',hook='前段與後段的距離，變近還是變遠',
   f=F2,sheet='Table I.B1.2a.42',cols=[3,7,11,15,19,23,27],cycles=SEVEN,hib=False,
   fmt='{v:.0f} 分',label='科學高低分差距（P90−P10）',rng=[190,320,1],
   q='2006 年臺灣前段與後段學生的科學分數差是 249 分。2025 年呢？',
   note='281 分，落到世界後段（同表第 83 名）。走勢很清楚：2006 年 249 分 → 2012 年縮到 215 分（最平等的一年）→ 之後一路擴大到 281 分。十三年來持續拉開。'),
 dict(id='t_top',teaser='頂尖學生的十九年',hook='世界級的臺灣學生變多還是變少',
   f=F2,sheet='Table I.B1.2a.33',cols=[3,7,11,15,19,23,27],cycles=SEVEN,hib=True,
   fmt='{v:.1f}%',label='科學頂尖學生（L5–6）比例',rng=[3,25,0.1],
   q='2006 年臺灣有 14.6% 的學生達到科學最高等級。2025 年這個比例是多少？',
   note='20.1%，世界第 3。從 2012 年的 8.3% 一路衝到 20.1%，十三年成長 2.4 倍。臺灣的頂端愈來愈強。'),
 dict(id='t_low',teaser='後段學生的十九年',hook='跟頂尖同時發生的另一件事',
   f=F2,sheet='Table I.B1.2a.33',cols=[1,5,9,13,17,21,25],cycles=SEVEN,hib=False,
   fmt='{v:.1f}%',label='科學未達基礎水準（L2 以下）比例',rng=[5,20,0.1],
   q='2012 年臺灣只有 9.8% 的學生沒達到科學基礎水準，是歷屆最低。2025 年呢？',
   note='12.9%。頂尖從 8.3% 漲到 20.1% 的同一段時間，後段也從 9.8% 漲到 12.9%。兩端一起長大——這就是上一題「差距擴大」的真正機制：不是後段崩盤，是前段跑太快。'),
 dict(id='t_gender',teaser='性別的十九年',hook='臺灣發生了一件其他國家沒發生的事',
   f=F4,sheet='Table I.B1.2c.25',cols=[1,7,13,19],cycles=[2015,2018,2022,2025],hib=None,flip=True,
   fmt='{v:+.1f} 分',label='科學成績性別差（女生減男生）',rng=[-25,25,0.5],
   q='2015 年臺灣男生的科學成績領先女生 4.5 分。2025 年的差距是多少？（正值代表女生領先）',
   note='女生領先 10.5 分。四屆走勢：男生 +4.5 → +1.2 → +3.4 → 女生 +10.5。臺灣在 2025 年翻盤，而且女生 545 分是世界第 3。同一屆的日本、美國仍是男生領先。'),
 dict(id='t_enjoy',teaser='樂趣的十年',hook='這題臺灣其實在變好',
   f=F6,sheet='Table I.B1.3.54',cols=[1,4],cycles=[2015,2025],hib=True,
   fmt='{v:+.2f}',label='享受科學（樂趣）指數',rng=[-0.6,0.6,0.01],
   q='2015 年臺灣學生「享受科學」的指數是 −0.06（低於 OECD 平均）。2025 年呢？',
   note='+0.05，回到 OECD 平均之上，十年進步 0.12。這是 OECD 用連結量尺算出的正式變化量。但排名幾乎沒動（第 53 → 第 57）——因為別人也在進步。'),
 dict(id='t_teacher',teaser='教師支持的十年',hook='全站進步幅度最大的一項',
   f=F7,sheet='Table I.B1.4.115',cols=[1,4],cycles=[2015,2025],hib=True,
   fmt='{v:+.2f}',label='科學課的教師支持指數',rng=[-0.4,0.7,0.01],
   q='2015 年臺灣「科學課教師支持」指數是 +0.06，只比 OECD 平均高一點。2025 年呢？',
   note='+0.33，十年進步 0.26，排名從第 41 名升到第 35 名。學生感受到的教師支持明顯提升——這是臺灣這十年少數大幅改善的項目。'),
 dict(id='t_escs',teaser='社經影響力的十年',hook='家庭背景的力量變大還是變小',
   f=F3,sheet='Table I.B1.2b.25',cols=[1,3,5,7],cycles=[2015,2018,2022,2025],hib=False,
   fmt='{v:.1f}%',label='社經地位可解釋的科學成績變異％',rng=[4,24,0.1],
   q='2015 年臺灣有 14.1% 的科學成績差異可以用家庭社經地位解釋。2025 年呢？',
   note='11.4%，略低於 OECD 的 11.6%，十年下降 2.6 個百分點。單看這個指標，臺灣的「家庭決定論」其實在鬆動——但別忘了城鄉分數差仍有 102 分，補習的社經落差仍是世界倒數第二。'),
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
      'tw':tw,'oecd':oecd,'ranks':ranks,
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
