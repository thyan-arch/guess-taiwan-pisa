# -*- coding: utf-8 -*-
"""挑出診斷型題目，輸出網頁用的精簡資料 data/web_data.json"""
import json, os, sys
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from qtext import RANK, TREND, MORE_WORD, NEUTRAL
from collections import defaultdict
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
db=json.load(open(os.path.join(ROOT,'data','pisa.json'),encoding='utf-8'))
meta,oecd=db['indicators'],db['oecd_average']
ZH={c['en']:c['zh'] for c in db['countries']}
idx=defaultdict(dict)
for r in db['records']: idx[(r['cycle'],r['indicator'])][r['country']]=r
TW='Chinese Taipei'
MARK=['Japan','Korea','United States','Singapore','Finland','B-S-J-Z (China)']

# (章節, cycle, indicator, 題目, 揭曉後的一句話解讀, 單位顯示法)
Q=[
 ('成績',2025,'sci_mean','臺灣 15 歲學生的科學平均分數，在全世界排第幾？',
  '三屆科學主測年（2006／2015／2025），臺灣都穩坐第 4 名。成績從來不是臺灣的問題。','{v:.0f} 分'),
 ('成績',2025,'pct_top','科學能力達到最高等級（L5–6）的「頂尖學生」比例，臺灣排第幾？',
  '每 5 個臺灣學生就有 1 個是世界頂尖，比例是 OECD 平均的近 3 倍。','{v:.1f}%'),
 ('成績',2025,'sci_spread','臺灣前段班與後段班的分數差距（P90−P10），在世界上排第幾？',
  '差距 281 分 ≈ 14 年的學習落差。而且一路擴大：2006 是 94 分標準差，2025 已經 107 分。','{v:.0f} 分'),
 ('自信',2025,'growth_mindset','「智力是天生的、沒辦法改變」——不同意這句話（＝有成長心態）的臺灣學生比例排第幾？',
  '只有 45.5% 的臺灣學生相信自己能變聰明。日本 76%、韓國 78%、愛沙尼亞 83%。這不是「東亞文化」，這是臺灣的獨有問題。','{v:.1f}%'),
 ('自信',2006,'self_concept','2006 年，臺灣學生的「科學自我概念」（我是不是讀科學的料）排第幾？',
  '同一年，臺灣學生的「科學自我效能」（我做得到這些科學任務）排第 7。做得到，但不覺得自己是那塊料。','{v:+.2f}'),
 ('自信',2025,'cognitive_adaptability','面對陌生、沒遇過的狀況時，臺灣學生的「認知彈性」排第幾？',
  '倒數第三，只贏日本與汶萊。會解熟悉的題，不會處理沒看過的狀況。','{v:+.2f}'),
 ('動機',2025,'enjoyment','臺灣學生「享受科學、覺得學科學有趣」的程度排第幾？',
  '三屆都在中後段：2006 第 22/57、2015 第 59/73、2025 第 57/91。成績世界第 4，樂趣一直是中等。','{v:+.2f}'),
 ('動機',2025,'curiosity','臺灣學生對世界的「好奇心」排第幾？',
  '好奇心低於 OECD 平均。這是科學教育最不該輸的一項。','{v:+.2f}'),
 ('動機',2015,'career_sci','2015 年，臺灣 15 歲學生「30 歲時想從事科學相關工作」的比例排第幾？',
  '20.9%，低於 OECD 的 24.5%。其中「想當醫療專業人員」只有 7.2%，全世界倒數第三。','{v:.1f}%'),
 ('性別',2025,'gender_gap_sci','臺灣科學成績的性別差距（女生減男生）排第幾？',
  '臺灣女生科學 545 分，男生 535 分——女生贏 10.5 分，世界第 3 高的女生成績。日本、美國仍是男生領先。','{v:+.1f} 分'),
 ('性別',2025,'sci_girls','只看女生，臺灣女生的科學成績在全世界排第幾？',
  '世界第 3，只輸中國四省市與新加坡。臺灣女生的科學表現是國際級的。','{v:.0f} 分'),
 ('城鄉',2025,'urban_rural_gap','臺灣城市學校與鄉村學校的科學分數差距，在世界上排第幾？',
  '差 102 分，OECD 平均只差 32 分。臺灣城市學校世界第 3（556 分），鄉村學校 454 分——低於 OECD 平均。','{v:.0f} 分'),
 ('城鄉',2025,'cram_ses_gap','「有上額外科學課／補習」這件事，臺灣優勢與弱勢家庭的差距排第幾？',
  '差 22 個百分點（優勢 80% vs 弱勢 59%），OECD 平均只差 3.4。補習把家庭差距直接放大成學習差距。','{v:+.1f} 個百分點'),
 ('城鄉',2025,'between_school_var','臺灣學生的科學成績差異，有多少比例是來自「學校之間」的不同？',
  '42% 來自學校之間，OECD 平均 31%，芬蘭只有 8%。你讀哪間學校，很大程度決定你的科學成績。','{v:.1f}%'),
 ('課堂',2025,'rel_infodecision','三個科學子項裡，臺灣在「評估科學資訊、做出決策」相對自己的總分表現，排第幾？',
  '比自己的平均低 11.4 分，倒數第四。2006 年也一樣：「辨識科學議題」倒數第二。二十年了，同一個病——會解釋，不會提問與判斷。','{v:+.1f} 分'),
 ('課堂',2025,'rel_explain','同樣三個子項裡，臺灣在「科學地解釋現象」相對自己總分的表現排第幾？',
  '比自己的平均高 4.4 分，世界第 5。臺灣學生最強的是「解釋老師教過的現象」。','{v:+.1f} 分'),
 ('課堂',2025,'cognitive_activation','科學課上，老師讓學生提出假設、設計實驗、討論不同解法的頻率（認知啟動），臺灣排第幾？',
  '低於 OECD 平均。課堂少讓學生自己提問設計，正好對應上一題的弱項。','{v:+.2f}'),
 ('課堂',2025,'discipline','臺灣科學課的秩序與紀律，在世界上排第幾？',
  '世界第 9。臺灣的課堂安靜、有秩序、幾乎不被手機干擾（科學課被數位裝置干擾比例世界第 8 低）。紀律不是問題。','{v:+.2f}'),
 ('課堂',2025,'life_satisfaction','臺灣 15 歲學生的生活滿意度（0–10 分）排第幾？',
  '6.72 分，第 76/85。成績世界第 4，快樂度世界後段。','{v:.2f} 分'),
]

out=[]
for grp,cyc,ind,q,note,fmt in Q:
    m=meta[f'{cyc}|{ind}']
    by=idx[(cyc,ind)]
    tw=by[TW]
    vals=sorted(((r['value'],c) for c,r in by.items()), reverse=(m['hib'] is not False))
    out.append({
      'type':'rank','group':grp,'cycle':cyc,'id':f'{cyc}_{ind}','q':RANK[ind]['q'],'note':note,'fmt':fmt,
      'teaser':RANK[ind]['teaser'],'hook':RANK[ind]['hook'],'what':RANK[ind]['what'],
      'label':m['zh'],'kind':m['kind'],'hib':m['hib'],
      'n':tw['n'],'rank':tw['rank'],'tw':tw['value'],
      'oecd':oecd.get(f'{cyc}|{ind}'),
      'dist':[round(v,3) for v,_ in vals],
      'marks':[{'zh':ZH.get(c,c),'v':by[c]['value'],'r':by[c]['rank']} for c in MARK if c in by],
      'best':{'zh':ZH.get(vals[0][1],vals[0][1]),'v':round(vals[0][0],3)},
      'worst':{'zh':ZH.get(vals[-1][1],vals[-1][1]),'v':round(vals[-1][0],3)},
      'src':m['source'],
      'moreWord':MORE_WORD.get(ind,'高'),'neutral':ind in NEUTRAL,
      'surprise':(None if ind=='sci_mean' else round(abs(
          100*(tw['rank']-1)/max(1,tw['n']-1)
          - 100*(idx[(cyc,'sci_mean')][TW]['rank']-1)/max(1,idx[(cyc,'sci_mean')][TW]['n']-1)),1)
          if TW in idx.get((cyc,'sci_mean'),{}) else None),
    })
json.dump(out,open(os.path.join(ROOT,'data','web_data.json'),'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(len(out),'題；檔案大小',os.path.getsize(os.path.join(ROOT,'data','web_data.json')),'bytes')
for o in out: print(f"  [{o['group']}] {o['label'][:22]:<24} 第{o['rank']}/{o['n']}")
