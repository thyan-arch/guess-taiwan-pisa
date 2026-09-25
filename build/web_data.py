# -*- coding: utf-8 -*-
"""挑出診斷型題目，輸出網頁用的精簡資料 data/web_data.json"""
import json, os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from qtext import RANK, TREND, MORE_WORD, NEUTRAL, POLES
from collections import defaultdict
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
db=json.load(open(os.path.join(ROOT,'data','pisa.json'),encoding='utf-8'))
meta,oecd=db['indicators'],db['oecd_average']
ZH={c['en']:c['zh'] for c in db['countries']}
idx=defaultdict(dict)
for r in db['records']: idx[(r['cycle'],r['indicator'])][r['country']]=r
TW='Chinese Taipei'
MARK=['Japan','Korea','United States','Singapore','Finland','B-S-J-Z (China)']

# (章節, cycle, indicator, 揭曉後的一句話解讀, 單位顯示法)；題目文字在 qtext.RANK
Q=[
 ('成績',2025,'sci_mean',
  '三個科學主測年（2006、2015、2025）臺灣都落在分數最高的那一端，每一屆都只有極少數國家比臺灣高。','{v:.0f} 分'),
 ('成績',2025,'pct_top',
  '20.1%，落在頂尖學生最多的那一端，約為 OECD 平均 7.2% 的 2.8 倍。','{v:.1f}%'),
 ('成績',2025,'sci_spread',
  '281 分，落在落差大的那一端。標準差同期也從 2006 年的 94 分增加到 2025 年的 107 分。PISA 估算 15 歲學生一年學習約值 20 分，但 OECD 提醒這個換算不宜機械套用在國內落差上。','{v:.0f} 分'),
 ('自信',2025,'growth_mindset',
  '只有 45.5% 的臺灣學生不同意這句話，顯著低於 OECD 平均的 69.3%，也低於日本 76.0% 與韓國 77.9%。不過同屬東亞的香港 44.1%、中國四省市 49.6% 同樣偏低，因此不宜單純解讀為臺灣獨有、或歸因於單一「東亞文化」。','{v:.1f}%'),
 ('自信',2006,'self_concept',
  '同一年，臺灣學生的「科學自我效能」（我做得到這些科學任務）卻落在很有把握的那一端。覺得自己做得到，但不覺得自己是那塊料。','{v:+.2f}'),
 ('自信',2025,'cognitive_adaptability',
  '落在應變最沒信心的那一端，只有日本與汶萊比臺灣更低。要注意這是學生對自己的評價，不是實際的應變能力。','{v:+.2f}'),
 ('動機',2025,'enjoyment',
  '2006 年還偏覺得有趣，2015 年落到不覺得有趣的那一端，2025 年回到中間偏不覺得有趣。成績三屆都在分數最高的那一端，樂趣卻一直沒跟上。','{v:+.2f}'),
 ('動機',2025,'curiosity',
  '複合指數 −0.13，低於 OECD 平均。但拆開三道題差很多：「我對很多事情都感到好奇」臺灣 73.2%、OECD 73.5%，幾乎一樣；「我比大多數人更好奇」臺灣 51.4%、OECD 53.5%，略低；落差主要來自「我喜歡知道事物如何運作」——臺灣 65.1%、OECD 74.0%，差 8.9 個百分點。因此不宜說臺灣學生整體比較不好奇。','{v:+.2f}'),
 ('動機',2015,'career_sci',
  '20.9%，低於 OECD 的 24.5%。其中「想當醫療專業人員」只有 7.2%，落在最少的那一端，只有兩個國家／經濟體比臺灣更少。','{v:.1f}%'),
 ('性別',2025,'gender_gap_sci',
  '臺灣女生科學 545 分，男生 535 分，女生領先 10.5 分。女生成績落在分數最高的那一端。同一屆的日本、美國仍是男生領先。','{v:+.1f} 分'),
 ('性別',2025,'sci_girls',
  '落在分數最高的那一端，只低於中國四省市與新加坡。','{v:.0f} 分'),
 ('城鄉',2025,'urban_rural_gap',
  '差 102 分，OECD 平均只差 32 分。臺灣城市學校 556 分，落在分數最高的那一端；鄉村學校 454 分，低於 OECD 平均的 458 分。','{v:.0f} 分'),
 ('城鄉',2025,'cram_ses_gap',
  '差 22 個百分點（優勢 80% vs 弱勢 59%），OECD 平均只差 3.4。補習把家庭差距直接放大成學習差距。','{v:+.1f} 個百分點'),
 ('城鄉',2025,'between_school_var',
  '42% 來自學校之間，OECD 平均 31%，芬蘭只有 8%。你讀哪間學校，很大程度決定你的科學成績。','{v:.1f}%'),
 ('課堂',2025,'rel_infodecision',
  '比臺灣自己的科學總分低 11.4 分，落在相對弱項的那一端。要注意這是「相對」強弱：臺灣這一項的絕對分數是 528 分，仍遠高於 OECD 平均的 480 分。它的意思是，在臺灣學生的三項科學能力當中，這一項相對最不突出——2006 年的「辨識科學議題」也是同樣的形狀。','{v:+.1f} 分'),
 ('課堂',2025,'rel_explain',
  '比臺灣自己的科學總分高 4.4 分，落在相對強項的那一端。也就是說，三項科學能力裡，「解釋現象」是臺灣相對最突出的一項。','{v:+.1f} 分'),
 ('課堂',2025,'cognitive_activation',
  '低於 OECD 平均。課堂少讓學生自己提問設計，正好對應上一題的弱項。','{v:+.2f}'),
 ('課堂',2025,'discipline',
  '落在課堂有秩序的那一端。臺灣的科學課安靜，被數位裝置干擾的比例也落在最低的那一群（13.2%，OECD 28.4%）。','{v:+.2f}'),
 ('課堂',2025,'life_satisfaction',
  '6.72 分，落在不滿意的那一端，低於 OECD 平均的 7.22 分。','{v:.2f} 分'),
]

out=[]
for grp,cyc,ind,note,fmt in Q:
    m=meta[f'{cyc}|{ind}']
    by=idx[(cyc,ind)]
    tw=by[TW]
    vals=sorted(((r['value'],c) for c,r in by.items()))          # 由低到高
    n=len(vals)
    def pos(c):   # 光譜位置 0–100：比它數值低的國家占多少
        v=by[c]['value']; return round(100*sum(1 for x,_ in vals if x<v)/max(1,n-1),1)
    out.append({
      'type':'rank','group':grp,'cycle':cyc,'id':f'{cyc}_{ind}','q':RANK[ind]['q'],'note':note,'fmt':fmt,
      'teaser':RANK[ind]['teaser'],'hook':RANK[ind]['hook'],'what':RANK[ind]['what'],
      'label':m['zh'],'kind':m['kind'],'hib':m['hib'],
      'n':tw['n'],'rank':tw['rank'],'tw':tw['value'],
      'oecd':oecd.get(f'{cyc}|{ind}'),
      'dist':[round(v,3) for v,_ in vals],
      'pos':pos(TW),'poles':POLES[ind],
      'marks':[{'zh':ZH.get(c,c),'v':by[c]['value'],'p':pos(c)} for c in MARK if c in by],
      'top':{'zh':ZH.get(vals[-1][1],vals[-1][1]),'v':round(vals[-1][0],3)},
      'bottom':{'zh':ZH.get(vals[0][1],vals[0][1]),'v':round(vals[0][0],3)},
      'src':m['source'],
      'moreWord':MORE_WORD.get(ind,'高'),'neutral':ind in NEUTRAL,
      'surprise':(None if ind=='sci_mean' else round(abs(
          100*(tw['rank']-1)/max(1,tw['n']-1)
          - 100*(idx[(cyc,'sci_mean')][TW]['rank']-1)/max(1,idx[(cyc,'sci_mean')][TW]['n']-1)),1)
          if TW in idx.get((cyc,'sci_mean'),{}) else None),
    })
json.dump(out,open(os.path.join(ROOT,'data','web_data.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(len(out),'題；檔案大小',os.path.getsize(os.path.join(ROOT,'data','web_data.json')),'bytes')
for o in out: print(f"  [{o['group']}] {o['label'][:22]:<24} 位置 {o['pos']:>5}（{o['poles'][0]}→{o['poles'][1]}）")
