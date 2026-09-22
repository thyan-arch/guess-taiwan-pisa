# -*- coding: utf-8 -*-
"""PISA 2025 題庫：從官方 Codebook 抽出所有問卷題項，
並從 Annex B 表接上「臺灣 vs OECD 的逐選項作答百分比」。"""
import os, re, json, csv
import openpyxl
from difflib import get_close_matches

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
RAW  = os.path.join(ROOT, 'raw')
ITM  = os.path.join(RAW, 'items')
OUT  = os.path.join(ROOT, 'data', 'items')
os.makedirs(OUT, exist_ok=True)

MISSING = {95, 96, 97, 98, 99, 995, 996, 997, 998, 999}
ITEM_RE = re.compile(r'^(ST|IC|EC|WB|FL|PA|SC|TC)\d{3}Q\d{2}')

# ---------------------------------------------------------------- Codebook
def parse_codebook():
    wb = openpyxl.load_workbook(os.path.join(ITM, 'PISA2025_Codebook.xlsx'),
                                read_only=True, data_only=True)
    out, indices = [], []
    PREFIX = {'ST': '學生問卷', 'IC': 'ICT 數位素養問卷', 'PA': '家長問卷',
              'EC': '學生問卷（教育歷程）', 'WB': '學生問卷（身心福祉）',
              'FL': '外語評量問卷', 'SC': '學校問卷', 'TC': '教師問卷'}
    for sheet, source in (('STU', '學生問卷'), ('SCH', '學校問卷'), ('TCH', '教師問卷')):
        if sheet not in wb.sheetnames: continue
        rows = [list(r) for r in wb[sheet].iter_rows(values_only=True)]
        for i, r in enumerate(rows):
            name = str(r[0]).strip() if r[0] else ''
            if not name: continue
            label = str(r[1]).strip() if r[1] else ''
            # 蒐集選項
            opts, j = [], i + 1
            while j < len(rows) and not rows[j][0]:
                v, lab = rows[j][5], rows[j][6]
                if v is not None and lab is not None:
                    try: iv = int(float(v))
                    except (TypeError, ValueError): iv = None
                    opts.append({'value': v if iv is None else iv,
                                 'label': str(lab).strip(),
                                 'missing': iv in MISSING if iv is not None else False})
                j += 1
            if ITEM_RE.match(name):
                stem, _, text = label.partition(' - ')
                out.append({
                    'code': name, 'block': name[:5],
                    'source': PREFIX.get(name[:2], source), 'file_sheet': sheet,
                    'stem_en': stem.strip(),
                    'text_en': (text or stem).strip(),
                    'options': [o for o in opts if not o['missing']],
                    'missing_codes': [o for o in opts if o['missing']],
                })
            elif label and ('(WLE)' in label or '(scale)' in label.lower()):
                indices.append({'code': name, 'label_en': label, 'source': source})
    return out, indices

# ---------------------------------------------------------------- Annex B 逐選項百分比
B_FILES = ['b1_1_2025.xlsx', 'b1_2_2025.xlsx', 'b1_3_2025.xlsx', 'b1_4_2025.xlsx',
           'b1_5_2025.xlsx', 'b1_6_2025.xlsx', 'b1_7_2025.xlsx', 'b1_8_2025.xlsx']

def loose(s):
    """去掉 <佔位符> 與括號補充後的寬鬆比對鍵"""
    s = re.sub(r'<[^>]*>', ' ', str(s))
    s = re.sub(r'\([^)]*\)', ' ', s)
    s = re.sub(r'[^0-9a-z\u4e00-\u9fff]+', ' ', s.lower())
    return re.sub(r'\s+', ' ', s).strip()

def norm(s):
    s = re.sub(r'<[^>]*>', '', str(s))
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    return re.sub(r'[\s ]+', ' ', s).strip().lower().rstrip('.')

def parse_annexb():
    """回傳 {正規化題目文字: {'table':…, 'index':…, 'dist':[{cat, tw, oecd}]}}"""
    found = {}
    for f in B_FILES:
        path = os.path.join(RAW, f)
        if not os.path.exists(path): continue
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        for sh in wb.sheetnames:
            if sh in ('TOC', 'About this file'): continue
            rows = []
            for k, r in enumerate(wb[sh].iter_rows(values_only=True)):
                rows.append(list(r))
                if k > 120: break
            oecd_i = next((k for k, r in enumerate(rows)
                           if r and r[0] and str(r[0]).strip() == 'OECD average'), None)
            if oecd_i is None or oecd_i < 3: continue
            tw_row = next((r for r in rows if r and r[0] and 'Taipei' in str(r[0])), None)
            if tw_row is None: continue
            r_unit, r_cat, r_item = rows[oecd_i-1], rows[oecd_i-2], rows[oecd_i-3]
            r_grp = []
            for back in range(3, 8):
                if oecd_i - back >= 0: r_grp += [x for x in rows[oecd_i-back] if x]
            title = str(rows[1][0]).strip() if len(rows) > 1 and rows[1][0] else sh
            idx_label = next((str(x).strip() for x in r_grp
                              if str(x).strip().startswith('Index of')), '')
            if not idx_label and title.startswith(('Students', 'Student ')):
                idx_label = ''
            cur_item, per_item = None, {}
            for c, u in enumerate(r_unit):
                if str(u).strip() != '%': continue
                if c < len(r_item) and r_item[c]: cur_item = str(r_item[c]).strip()
                if not cur_item or len(cur_item) < 12: continue
                cat = str(r_cat[c]).strip() if c < len(r_cat) and r_cat[c] else ''
                if not cat: continue
                tw = tw_row[c] if c < len(tw_row) else None
                oe = rows[oecd_i][c] if c < len(rows[oecd_i]) else None
                if not isinstance(tw, (int, float)) or not isinstance(oe, (int, float)): continue
                per_item.setdefault(cur_item, []).append(
                    {'category': cat, 'taiwan': round(tw, 2), 'oecd': round(oe, 2)})
            for item, dist in per_item.items():
                rec = {'table': sh, 'table_title': title,
                       'index_label': idx_label, 'dist': dist, 'file': f}
                for key in (norm(item), loose(item)):
                    if key: found.setdefault(key, []).append(rec)
    return found

# 同一題會出現在多張表（交叉分析、變化量、相關）；挑出「主表」
_PENAL = ('by student', 'by school', 'and other', 'change between', 'relationship',
          'and science performance', 'and performance', 'across', 'and attitudes',
          ', 20', 'through 20', 'and computational', 'by level of', 'by gender',
          'by teacher', 'by family', 'by parental', 'profiles', 'and learning')
def primary(recs):
    def score(r):
        t = r['table_title'].lower()
        pen = sum(8 for w in _PENAL if w in t)
        num = re.findall(r'(\d+)$', r['table'])
        return (pen, int(num[0]) if num else 999)
    return sorted(recs, key=score)[0]

# ---------------------------------------------------------------- 組裝
_loose_keys = []

def main():
    items, indices = parse_codebook()
    print(f'Codebook：{len(items)} 個問卷題項、{len(indices)} 個衍生指數')
    annex = parse_annexb()
    global _loose_keys
    _loose_keys = list(annex.keys())
    print(f'Annex B：{len(annex)} 個題目有逐選項百分比')

    matched = 0
    for it in items:
        recs = annex.get(norm(it['text_en'])) or annex.get(loose(it['text_en']))
        if not recs:
            lk = loose(it['text_en'])
            if len(lk) > 18:
                near = get_close_matches(lk, _loose_keys, n=1, cutoff=0.86)
                if near: recs = annex.get(near[0])
        hit = primary(recs) if recs else None
        if hit:
            matched += 1
            it['annex_table'] = hit['table']
            it['annex_title'] = hit['table_title']
            ct = re.split(r',\s*by\s+', hit['table_title'])[0].strip()
            it['construct'] = ct
            it['index_label'] = hit['index_label']
            it['distribution'] = hit['dist']
    print(f'對上 Annex B 的題項：{matched} / {len(items)}')

    # 同一題組屬同一構念：以組內出現最多的構念補齊全組
    from collections import Counter
    by_block = {}
    for it in items: by_block.setdefault(it['block'], []).append(it)
    for blk, its in by_block.items():
        cs = Counter(x['construct'] for x in its if x.get('construct'))
        if not cs: continue
        top = cs.most_common(1)[0][0]
        tbl = next((x.get('annex_table') for x in its if x.get('construct') == top), '')
        for x in its:
            if not x.get('construct'):
                x['construct'] = top
                x['construct_inferred'] = True
                if tbl: x.setdefault('annex_table', tbl)
    items.sort(key=lambda x: x['code'])
    json.dump({'meta': {'cycle': 2025, 'built': '2026-09-22',
                        'source': 'OECD PISA 2025 Codebook + PISA 2025 Results (Volume I) Annex B',
                        'n_items': len(items)},
               'indices': indices, 'items': items},
              open(os.path.join(OUT, 'pisa2025_questionnaire_items.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    with open(os.path.join(OUT, 'pisa2025_questionnaire_items.csv'), 'w',
              newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['題項代碼', '題組', '問卷', '題幹（英文原文）', '題目（英文原文）',
                    '選項（依序）', '對應構念', 'Annex B 表', '臺灣各選項%', 'OECD各選項%'])
        for it in items:
            d = it.get('distribution') or []
            w.writerow([it['code'], it['block'], it['source'], it['stem_en'], it['text_en'],
                        ' | '.join(o['label'] for o in it['options']),
                        it.get('construct', ''), it.get('annex_table', ''),
                        ' | '.join(f"{x['category']}={x['taiwan']}" for x in d),
                        ' | '.join(f"{x['category']}={x['oecd']}" for x in d)])
    print('已輸出 data/items/pisa2025_questionnaire_items.{json,csv}')
    return items, indices

if __name__ == '__main__':
    main()
