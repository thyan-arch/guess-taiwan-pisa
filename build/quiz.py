# -*- coding: utf-8 -*-
"""從 pisa.json 產生互動問答用的資料層：
   - data/taiwan_profile.json  台灣逐指標的值／排名／OECD 對照／意外指數
   - data/quiz.json            可直接餵給網頁的題庫（含選項、正解、解說）
"""
import json, os
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
db = json.load(open(os.path.join(ROOT, 'data', 'pisa.json'), encoding='utf-8'))
recs, meta, oecd = db['records'], db['indicators'], db['oecd_average']

idx = defaultdict(dict)                      # (cycle,ind) -> country -> rec
for r in recs: idx[(r['cycle'], r['indicator'])][r['country']] = r
TW = 'Chinese Taipei'
REF = ['Japan', 'Korea', 'Singapore', 'B-S-J-Z (China)', 'Finland',
       'United States', 'Estonia', 'Hong Kong (China)']

def unit_of(kind):
    return {'score': '分', 'pct': '%', 'index': '（指數）', 'hours': '小時', 'points10': '分（0–10）', 'count': '人'}.get(kind, '')

# ---------------------------------------------------------- 台灣 profile
profile = []
for (cyc, ind), bycountry in idx.items():
    if TW not in bycountry: continue
    m = meta[f'{cyc}|{ind}']
    tw = bycountry[TW]
    sci = idx.get((cyc, 'sci_mean'), {}).get(TW)
    surprise = None
    if sci and ind != 'sci_mean':
        surprise = round(tw['pct_rank'] - sci['pct_rank'], 1)   # 正=比成績表現差
    top = sorted(bycountry.values(), key=lambda r: r['rank'])[:3]
    bottom = sorted(bycountry.values(), key=lambda r: -r['rank'])[:3]
    profile.append({
        'cycle': cyc, 'indicator': ind, 'group': m['group'], 'zh': m['zh'], 'en': m['en'],
        'kind': m['kind'], 'unit': unit_of(m['kind']), 'higher_is_better': m['hib'],
        'taiwan_value': tw['value'], 'taiwan_rank': tw['rank'], 'n': tw['n'],
        'taiwan_pct_rank': tw['pct_rank'],
        'oecd_average': oecd.get(f'{cyc}|{ind}'),
        'surprise': surprise,
        'top3': [{'country': r['country'], 'value': r['value']} for r in top],
        'bottom3': [{'country': r['country'], 'value': r['value']} for r in bottom],
        'reference': {c: bycountry[c]['value'] for c in REF if c in bycountry},
        'source': m['source'],
    })
profile.sort(key=lambda p: (p['cycle'], -(abs(p['surprise']) if p['surprise'] is not None else -1)))
json.dump(profile, open(os.path.join(ROOT, 'data', 'taiwan_profile.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# ---------------------------------------------------------- 題庫
def band(rank, n):
    """把排名轉成四個猜測區間"""
    q = rank / n
    if q <= 0.15: return 'A'
    if q <= 0.40: return 'B'
    if q <= 0.70: return 'C'
    return 'D'

BANDS = [('A', '世界前段（前 15%）'), ('B', '中上（15–40%）'),
         ('C', '中後段（40–70%）'), ('D', '後段（後 30%）')]

questions = []
for p in profile:
    n, rank = p['n'], p['taiwan_rank']
    correct = band(rank, n)
    cut = [max(1, round(n * 0.15)), round(n * 0.40), round(n * 0.70)]
    questions.append({
        'id': f"{p['cycle']}_{p['indicator']}",
        'cycle': p['cycle'], 'group': p['group'],
        'question': f"PISA {p['cycle']}：在參與的 {n} 個國家／經濟體中，臺灣的「{p['zh']}」排第幾？",
        'short': p['zh'],
        'options': [{'key': k, 'label': lab,
                     'range': [1 if k=='A' else (cut[0]+1 if k=='B' else (cut[1]+1 if k=='C' else cut[2]+1)),
                               cut[0] if k=='A' else (cut[1] if k=='B' else (cut[2] if k=='C' else n))]}
                    for k, lab in BANDS],
        'answer': correct,
        'answer_rank': rank, 'n': n,
        'taiwan_value': p['taiwan_value'], 'unit': p['unit'],
        'oecd_average': p['oecd_average'],
        'higher_is_better': p['higher_is_better'],
        'surprise': p['surprise'],
        'top3': p['top3'], 'bottom3': p['bottom3'], 'reference': p['reference'],
        'source': p['source'],
    })

# 意外度排序（給網頁預設出題順序用）
ranked = sorted([q for q in questions if q['surprise'] is not None],
                key=lambda q: -abs(q['surprise']))
json.dump({'questions': questions,
           'most_surprising': [q['id'] for q in ranked[:30]]},
          open(os.path.join(ROOT, 'data', 'quiz.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

print(f'台灣 profile：{len(profile)} 筆；題庫：{len(questions)} 題\n')
print('=== 意外指數 TOP 25（台灣在該面向的相對位置 vs 科學成績的相對位置）===')
for q in ranked[:25]:
    s = q['surprise']
    arrow = '↓落後' if s > 0 else '↑領先'
    o = q['oecd_average']
    print(f"  {q['cycle']} [{q['group']}] {q['short'][:24]:<26} "
          f"第{q['answer_rank']:>2}/{q['n']:<3} 台={q['taiwan_value']:>7.2f} "
          f"OECD={o:>7.2f} 意外{arrow}{abs(s):.0f}分位")
