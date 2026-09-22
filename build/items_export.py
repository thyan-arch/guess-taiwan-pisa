# -*- coding: utf-8 -*-
"""把題庫依問卷／構念分類匯出成資料夾（中英對照）"""
import os, re, json, csv, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl
from zh_items import OPT_ZH, STEM_ZH, ITEM_ZH, CONSTRUCT_ZH, BLOCK_ZH

# 官方臺灣國家版中文（若已解壓 Chinese Taipei.zip 並跑過 parse_zh_pdf.py）
_of = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'items', 'official_zh.json')
OFFICIAL = json.load(open(_of, encoding='utf-8')) if os.path.exists(_of) else {'items': {}, 'stems': {}}
OFF_ITEM, OFF_STEM = OFFICIAL.get('items', {}), OFFICIAL.get('stems', {})

def zh_text(it):
    """回傳 (中文, 來源)：官方優先，其次本專案翻譯"""
    o = OFF_ITEM.get(it['code'])
    if o: return o, '官方'
    t = ITEM_ZH.get(it['code'], '')
    return (t, '本專案翻譯') if t else ('', '')

def zh_stem(block):
    o = OFF_STEM.get(block)
    if o: return o, '官方'
    t = STEM_ZH.get(block, '')
    return (t, '本專案翻譯') if t else ('', '')

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
SRC  = os.path.join(ROOT, 'data', 'items', 'pisa2025_questionnaire_items.json')
BASE = os.path.join(ROOT, 'data', 'items')

FOLDER = {'學生問卷': '01_學生問卷', 'ICT 數位素養問卷': '02_ICT數位素養問卷',
          '家長問卷': '03_家長問卷', '學校問卷': '04_學校問卷', '教師問卷': '05_教師問卷'}

def safe(s):
    return re.sub(r'[\\/:*?"<>|]', '_', s).strip()[:60]

def zh_opt(label):
    return OPT_ZH.get(label.strip(), '')

def md_item(it, n):
    zh, src = zh_text(it)
    tag = {'官方': '', '本專案翻譯': '（本專案翻譯）'}.get(src, '')
    lines = [f"**{n}. {zh or it['text_en']}**{tag}", '']
    if zh: lines.append(f"　　原文：{it['text_en']}")
    lines.append(f"　　代碼：`{it['code']}`")
    d = it.get('distribution')
    if d:
        lines += ['', '　　| 選項 | 臺灣 | OECD |', '　　|---|--:|--:|']
        for x in d:
            c = zh_opt(x['category']) or x['category']
            lines.append(f"　　| {c} | {x['taiwan']}% | {x['oecd']}% |")
    lines.append('')
    return '\n'.join(lines)

def write_group(path, title_zh, title_en, items, note=''):
    b = items[0]['block']
    stem_zh, stem_src = zh_stem(b)
    stem_en = items[0]['stem_en']
    opts = items[0]['options']
    out = [f'# {title_zh}', '']
    if title_en: out.append(f'**Annex B 表標題（英文原文）**：{title_en}  ')
    out += [f'**題組代碼**：`{b}`　**題數**：{len(items)}　**問卷**：{items[0]["source"]}  ',
            f'**Annex B 表**：{items[0].get("annex_table", "—")}', '']
    if note: out += [note, '']
    out += ['## 題幹', '', f'> {stem_zh}' if stem_zh else '', '']
    if stem_zh: out.append(f'> 原文：{stem_en}')
    else: out.append(f'> {stem_en}')
    out += ['', '## 選項量尺', '']
    out.append(' ｜ '.join(f'{zh_opt(o["label"]) or o["label"]}（{o["label"]}）' for o in opts) or '（開放填答）')
    out += ['', '## 題目', '']
    for i, it in enumerate(items, 1):
        out.append(md_item(it, i))
    out += ['---', '',
            '資料：OECD PISA 2025 Codebook（題目原文與選項）＋ PISA 2025 Results (Volume I) Annex B（臺灣與 OECD 百分比）。',
            '中文優先採用 OECD 臺灣國家版問卷（Chinese Taipei StQ/IcQ/ScQ/TcQ/PaQ, zh-TW）的官方題目文字；',
            '標註「（本專案翻譯）」者為臺灣版未涵蓋、由本專案翻譯。〈尖括號〉為 PISA 在地化佔位符。']
    open(path, 'w', encoding='utf-8').write('\n'.join(out))

def main():
    db = json.load(open(SRC, encoding='utf-8'))
    items = db['items']
    for d in FOLDER.values():
        p = os.path.join(BASE, d)
        if os.path.isdir(p): shutil.rmtree(p)
        os.makedirs(p, exist_ok=True)
    os.makedirs(os.path.join(BASE, '00_總表'), exist_ok=True)
    os.makedirs(os.path.join(BASE, '06_認知測驗'), exist_ok=True)

    # ---- 各問卷：依構念（無構念者依題組）分檔 ----
    counts = {}
    for src, folder in FOLDER.items():
        sub = [x for x in items if x['source'] == src]
        if not sub: continue
        groups = {}
        for it in sub:
            key = it.get('construct') or f"__{it['block']}"
            groups.setdefault(key, []).append(it)
        made = 0
        for key, its in sorted(groups.items()):
            its.sort(key=lambda x: x['code'])
            if key.startswith('__'):
                blk = its[0]['block']
                topic = BLOCK_ZH.get(blk, '')
                zh = STEM_ZH.get(blk, '')
                name = f"{topic}（{blk}）" if topic else f"{blk}_{its[0]['stem_en'][:28]}"
                title_zh = topic or f"{blk}　{(zh or its[0]['stem_en'])[:40]}"
                title_en = ''
            else:
                zh = CONSTRUCT_ZH.get(key, key)
                name = f"{zh}"
                title_zh, title_en = zh, key
            write_group(os.path.join(BASE, folder, safe(name) + '.md'),
                        title_zh, title_en, its)
            made += 1
        # 該問卷總表 CSV
        with open(os.path.join(BASE, folder, '_總表.csv'), 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(['代碼', '題組', '構念（中）', '構念（英）', '題幹（中）', '題幹（英）',
                        '題目（中）', '中文來源', '題目（英）', '選項（中）', '選項（英）',
                        '臺灣各選項%', 'OECD各選項%', 'Annex B 表'])
            for it in sorted(sub, key=lambda x: x['code']):
                d = it.get('distribution') or []
                con = it.get('construct', '')
                _zh, _src = zh_text(it)
                w.writerow([it['code'], it['block'], CONSTRUCT_ZH.get(con, ''), con,
                            zh_stem(it['block'])[0], it['stem_en'],
                            _zh, _src, it['text_en'],
                            ' | '.join(zh_opt(o['label']) or o['label'] for o in it['options']),
                            ' | '.join(o['label'] for o in it['options']),
                            ' | '.join(f"{zh_opt(x['category']) or x['category']}={x['taiwan']}" for x in d),
                            ' | '.join(f"{zh_opt(x['category']) or x['category']}={x['oecd']}" for x in d),
                            it.get('annex_table', '')])
        counts[src] = (len(sub), made)

    # ---- 總表 ----
    with open(os.path.join(BASE, '00_總表', '問卷題庫_全部.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['代碼', '問卷', '題組', '構念（中）', '構念（英）', '題幹（中）', '題幹（英）',
                    '題目（中）', '中文來源', '題目（英）', '選項（英）',
                    '臺灣各選項%', 'OECD各選項%', 'Annex B 表'])
        for it in sorted(items, key=lambda x: (x['source'], x['code'])):
            d = it.get('distribution') or []
            con = it.get('construct', '')
            _zh, _src = zh_text(it)
            w.writerow([it['code'], it['source'], it['block'], CONSTRUCT_ZH.get(con, ''), con,
                        zh_stem(it['block'])[0], it['stem_en'],
                        _zh, _src, it['text_en'],
                        ' | '.join(o['label'] for o in it['options']),
                        ' | '.join(f"{x['category']}={x['taiwan']}" for x in d),
                        ' | '.join(f"{x['category']}={x['oecd']}" for x in d),
                        it.get('annex_table', '')])
    for it in items:
        it['text_zh'], it['text_zh_source'] = zh_text(it)
        it['stem_zh'] = zh_stem(it['block'])[0]
        it['construct_zh'] = CONSTRUCT_ZH.get(it.get('construct', ''), '')
    json.dump(db, open(os.path.join(BASE, '00_總表', '問卷題庫_全部.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    with open(os.path.join(BASE, '00_總表', '衍生指數清單.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['指數變項', '說明（英文原文）', '問卷'])
        for i in db['indices']: w.writerow([i['code'], i['label_en'], i['source']])

    # ---- 認知測驗題組清單 ----
    wb = openpyxl.load_workbook(os.path.join(ROOT, 'raw', 'items', 'PISA2025_Codebook.xlsx'),
                                read_only=True, data_only=True)
    rows = [list(r) for r in wb['COG'].iter_rows(values_only=True)]
    pat = re.compile(r'^([CD])([A-Z]*)([SRM])(\d{3}|[A-Z]*\d{3})Q(\d{2})')
    units = {}
    for r in rows[1:]:
        if not r[0] or not r[1] or ' - Q' not in str(r[1]): continue
        unit, _, q = str(r[1]).partition(' - ')
        m = re.match(r'^Q(\d+)', q)
        dom = {'S': '科學', 'R': '閱讀', 'M': '數學'}.get(
            next((c for c in str(r[0])[:6] if c in 'SRM'), ''), '其他')
        u = units.setdefault(unit.strip(), {'domain': dom, 'qs': set(), 'vars': 0})
        if m: u['qs'].add(int(m.group(1)))
        u['vars'] += 1
    with open(os.path.join(BASE, '06_認知測驗', '認知測驗題組清單.csv'), 'w',
              newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f); w.writerow(['題組名稱', '領域', '小題數', '小題編號', '資料變項數'])
        for name, u in sorted(units.items()):
            w.writerow([name, u['domain'], len(u['qs']),
                        ', '.join(f'Q{q:02d}' for q in sorted(u['qs'])), u['vars']])
    print(f'認知測驗題組：{len(units)} 個')
    for src, (n, g) in counts.items(): print(f'  {src}: {n} 題 → {g} 個分類檔')
    return units

if __name__ == '__main__':
    main()
