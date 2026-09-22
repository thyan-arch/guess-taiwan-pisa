# -*- coding: utf-8 -*-
"""解析 OECD 臺灣國家版中文問卷 PDF，抽出每個題項代碼對應的官方中文題目文字。"""
import os, re, sys, json, glob
import pypdf

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ZH   = os.path.join(ROOT, 'raw', 'items', 'zh_official')

CODE = re.compile(r'\b((?:ST|IC|EC|WB|FL|PA|SC|TC)\d{3}Q\d{2}[A-Z]{0,2}(?:_[AB])?)\b')
BLOCK = re.compile(r'(?:^|\n)\s*((?:ST|IC|EC|WB|FL|PA|SC|TC)\d{3})\s+(?!Q)([^\n]{4,200})')
CJK = r'　-〿一-鿿＀-￯'

def clean(s):
    s = s.replace('　', ' ')
    s = re.sub(r'□\s*\d+', ' ', s)          # 勾選方格
    s = re.sub(r'PISA 2025[^\n]*', ' ', s)  # 頁首
    s = re.sub(r'（?每一項請選擇一個答案。?）?', ' ', s)
    s = re.sub(r'（?請選擇一個答案。?）?', ' ', s)
    s = re.sub(r'\s*\n\s*', '', s)          # 換行直接接起來（中文不需空格）
    s = re.sub(rf'(?<=[{CJK}])\s+(?=[{CJK}])', '', s)   # 中文字之間的空白
    s = re.sub(r'\s{2,}', ' ', s)
    return s.strip(' \t·。').strip()

def page_text(path):
    r = pypdf.PdfReader(path)
    out = []
    for p in r.pages:
        try: out.append(p.extract_text() or '')
        except Exception: out.append('')
    return '\n'.join(out)

def parse(path):
    txt = page_text(path)
    # 題幹
    stems = {}
    for m in BLOCK.finditer(txt):
        blk, rest = m.group(1), m.group(2)
        c = clean(rest)
        if len(c) >= 4 and re.search(rf'[{CJK}]', c):
            stems.setdefault(blk, c)
    # 題目：每個代碼到下一個代碼（或方格）之間的文字
    hits = list(CODE.finditer(txt))
    per_code = {}
    for i, m in enumerate(hits):
        start = m.end()
        end = hits[i+1].start() if i+1 < len(hits) else min(len(txt), start + 400)
        seg = txt[start:end]
        # 只取第一個方格之前的文字
        box = seg.find('□')
        body = seg[:box] if box != -1 else seg
        c = clean(body)
        if c: per_code.setdefault(m.group(1), []).append(c)
    items, options = {}, {}
    for code, vals in per_code.items():
        uniq = [v for v in vals if v]
        if not uniq: continue
        if len(uniq) == 1:
            items[code] = uniq[0]
        else:
            # 同一代碼多次出現＝單選題，這些是選項標籤
            first = uniq[0]
            longest = max(uniq, key=len)
            if len(longest) > 2 * max(1, sum(len(u) for u in uniq[1:]) / max(1, len(uniq)-1)):
                items[code] = longest
                options[code] = [u for u in uniq if u != longest]
            else:
                options[code] = uniq
    return stems, items, options

def codebook_codes():
    """題庫的完整代碼，用來把 PDF 裡的短代碼（PA002Q01）對回 PA002Q01TA"""
    f = os.path.join(ROOT, 'data', 'items', 'pisa2025_questionnaire_items.json')
    if not os.path.exists(f): return {}, set()
    db = json.load(open(f, encoding='utf-8'))
    full = {x['code'] for x in db['items']}
    short = {}
    for c in full:
        m = re.match(r'^((?:ST|IC|EC|WB|FL|PA|SC|TC)\d{3}Q\d{2})', c)
        if m: short.setdefault(m.group(1), []).append(c)
    return short, full

def main():
    res = {'stems': {}, 'items': {}, 'options': {}, 'unmatched': {}, 'files': []}
    SHORT, FULL = codebook_codes()
    pdfs = sorted(glob.glob(os.path.join(ZH, '**', '*.pdf'), recursive=True))
    extra = os.path.join(ROOT, 'raw', 'items', 'student_questionnaire_zhTW.pdf')
    if os.path.exists(extra): pdfs.append(extra)   # 家長問卷（PaQ zh-TW）
    for p in pdfs:
        s, i, o = parse(p)
        res['files'].append({'file': os.path.basename(p), 'stems': len(s), 'items': len(i)})
        for k, v in s.items(): res['stems'].setdefault(k, v)
        for k, v in i.items():
            if k in FULL or not SHORT:
                res['items'].setdefault(k, v)
                continue
            # 只有「PDF 完全沒有字母後綴」時才允許用題號對應。
            # 國家版會沿用同一題號但換成不同後綴代表不同題目
            # （例：臺灣 PA003Q21JA ≠ 國際 PA003Q21DA），硬對會張冠李戴。
            m = re.fullmatch(r'((?:ST|IC|EC|WB|FL|PA|SC|TC)\d{3}Q\d{2})', k)
            if not m: 
                res['unmatched'] = res.get('unmatched', {})
                res['unmatched'][k] = v
                continue
            cands = SHORT.get(m.group(1), [])
            if len(cands) == 1:
                res['items'].setdefault(cands[0], v)
            else:
                res.setdefault('unmatched', {})[k] = v
        for k, v in o.items(): res['options'].setdefault(k, v)
        print(f'  {os.path.basename(p):<42} 題幹 {len(s):>3}　題目 {len(i):>4}')
    out = os.path.join(ROOT, 'data', 'items', 'official_zh.json')
    json.dump(res, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'\n合計：題幹 {len(res["stems"])}、對上代碼的題目 {len(res["items"])}'
          f'、代碼對不上（國家版自有題號）{len(res.get("unmatched", {}))}'
          f' → data/items/official_zh.json')

if __name__ == '__main__':
    main()
