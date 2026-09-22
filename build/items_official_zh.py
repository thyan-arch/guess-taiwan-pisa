# -*- coding: utf-8 -*-
"""若使用者手動下載了 OECD 的 Chinese Taipei.zip，解出裡面的中文題本。"""
import os, sys, zipfile
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ITM = os.path.join(ROOT, 'raw', 'items')
OUT = os.path.join(ITM, 'zh_official')

def main():
    cand = [f for f in os.listdir(ITM) if f.lower().endswith('.zip') and 'taipei' in f.lower()]
    if not cand:
        print('找不到 Chinese Taipei.zip。')
        print('請到 https://www.oecd.org/en/data/datasets/pisa-2025-database.html')
        print('→ National versions → Chinese Taipei，用瀏覽器下載後放進 raw/items/')
        return 1
    z = os.path.join(ITM, cand[0])
    if not zipfile.is_zipfile(z):
        print(f'{cand[0]} 不是有效的 zip（很可能是 Cloudflare 擋下的 HTML）。請用瀏覽器重新下載。')
        return 1
    os.makedirs(OUT, exist_ok=True)
    with zipfile.ZipFile(z) as f:
        names = f.namelist()
        f.extractall(OUT)
    print(f'已解壓 {len(names)} 個檔案到 raw/items/zh_official/：')
    for n in names: print('  ', n)
    return 0

if __name__ == '__main__':
    sys.exit(main())
